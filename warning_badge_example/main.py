#
# * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# * SPDX-License-Identifier: MIT-0
# *
# * Permission is hereby granted, free of charge, to any person obtaining a copy of this
# * software and associated documentation files (the "Software"), to deal in the Software
# * without restriction, including without limitation the rights to use, copy, modify,
# * merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# * permit persons to whom the Software is furnished to do so.
# *
# * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# * INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# * PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
###################################################################################################
# Imports

# MicroPython native libraries
import os
import sys
import time
import ujson
import machine
import network
import ntptime
import bluetooth
from umqtt.simple import MQTTClient

# Imported libraries
from ble_advertising import advertising_payload

# Device-specific libraries
import m5
from m5 import *

###################################################################################################
# Parameters

WIFI_SSID       = 'Wifi_name'                   # WiFi SSID name, 2.4GHz only, not compatible with 5GHz networks
WIFI_PASS       = 'Wifi_password'               # WiFi password
BADGE_NO        = '1'                           # Define the badge number, in case there are multiple badges in the same AWS account
THING_NAME      = 'WarningBadge_' + BADGE_NO    # The Thing Name registered on AWS
SHADOW_NAME     = 'WarningBadge'                # The named shadow created on AWS
AWS_ENDPOINT    = 'xxxxxxxxxxxxxx-ats.iot.us-east-1.amazonaws.com'  # The AWS IoT Endpoint for your region
AWS_PUB_TOPIC   = 'EduKit/WarningBadge/{}/up'.format(BADGE_NO)      # MQTT topic for badge to publish to
AWS_SUB_TOPIC_1 = 'EduKit/WarningBadge/{}/down'.format(BADGE_NO)    # MQTT topic to subscribe to for badge-specific messages
AWS_SUB_TOPIC_2 = 'EduKit/WarningBadge'                             # MQTT topic to subscribe to for messages for all badges
UART_UUID       = "6E400001-B5A3-F393-E0A9-E10E24DCCAAA"            # Unique UUID for the BLE adapter, change for each device

SHADOW_TOPIC    = '$aws/things/{}/shadow/name/{}/'.format(THING_NAME, SHADOW_NAME)  # MQTT topic to communicate with the named shadow
AWS_PUB_FREQ    = 1                             # Frequency at which to publish messages to AWS, in seconds

# Temporary parameters until UIFlow 2 supports all EduKit functionality
AWS_PRIVATE_KEY = '/flash/certs/private.pem.key'        # Path to the AWS private key generated when creating the IoT Thing
AWS_CERTIFICATE = "/flash/certs/certificate.pem.crt"    # Path to the AWS certificate generated
NTP_TIME_SHIFT  = 946684799     # Time correction from NTP time to ETC, potentially different for each user
RESET_TIMER     = 1             # Frequency at which to reset the device, temporary solution to work around memory leaks and connectivity issues

SAFE            = 0             # Value for safe conditions
ALARM           = 1             # Value for alarm conditions

###################################################################################################
# Setup

# Helper functions for device
m5.begin()

# Clear the screen to all-white
lcd.clear(0xFFFFFF)

# Set the default font type and color
lcd.setFont(display.FONT_DejaVu24)
lcd.setTextColor(lcd.BLACK)

###################################################################################################
# Functions

# Setup WiFi connection
def connectWifi():
    print('Wifi activating...')
    wlan.active(True)
    if not wlan.isconnected():
        print('Wifi connecting...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            pass
        print('Wifi connected, network config: {}'.format(wlan.ifconfig()))
    time.sleep(1)
    return


# Connect to AWS IoT Core
def connectAWSIoT():
    print('AWS IoT starting MQTT connection...')
    response = mqtt.connect()
    print('AWS IoT connected. Response={}'.format(response))
    time.sleep(1)
    return


# Reconnect WiFi
def reconnect():
    print('Reconnecting to WiFi and AWS...')
    if not wlan.isconnected():
        print('Wifi connecting...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            pass
        print('Wifi connected, network config: {}'.format(wlan.ifconfig()))
    time.sleep(1)

    print('AWS IoT starting MQTT connection...')
    response = mqtt.connect()
    print('AWS IoT connected. Response={}'.format(response))
    time.sleep(1)
    return


# Subcribe to MQTT topic
def subListener(top, msg):
    global alarm_state

    topic = top.decode()
    message = ujson.loads(msg)
    
    # Process each topic separately
    if topic == AWS_SUB_TOPIC_1:
        if message['command'] == 'enter_alarm':
            alarm_state = ALARM
        if message['command'] == 'exit_alarm':
            alarm_state = SAFE
        
    elif topic == AWS_SUB_TOPIC_2:
        if message['command'] == 'enter_alarm':
            alarm_state = ALARM
        if message['command'] == 'exit_alarm':
            alarm_state = SAFE
            
    elif topic == SHADOW_TOPIC + 'get/accepted':
        alarm_state = message['state']['desired']['alarm_state']
        
    return


# Start Bluetooth advertising
def startBluetoothAdvertising():
    ble.active(True)
    payload = advertising_payload(name="Badge {}".format(BADGE_NO), services=[bluetooth.UUID(UART_UUID)])
    interval_us = 500000
    ble.gap_advertise(interval_us, adv_data=payload)
    return

###################################################################################################
# Main

# Load certificates
print('SSL parameters loading...')
with open(AWS_PRIVATE_KEY, 'r') as f:
    key = f.read()
with open(AWS_CERTIFICATE, 'r') as f:
    cert = f.read()

ssl_params = {'key': key, 'cert': cert, 'server_side': False}
print('SSL parameters loaded.')

# Initialize clients for WiFi, MQTT and BLE
wlan = network.WLAN(network.STA_IF)
mqtt = MQTTClient(THING_NAME, AWS_ENDPOINT, port=8883, keepalive=10000, ssl=True, ssl_params=ssl_params)
ble = bluetooth.BLE()

# Start Bluetooth
startBluetoothAdvertising()

# Connect to WiFi
connectWifi()

# Get NTP time
while True:
    try:
        ntptime.settime()
        break
    except Exception as e:
        print('Failed to get NPT time, trying again...')
        time.sleep(1)
        
# Connect to AWS IoT Core
connectAWSIoT()

# Initialize variables
alarm_state = SAFE
start_time = time.time()

# Setup MQTT topics
mqtt.set_callback(subListener)
mqtt.subscribe(AWS_SUB_TOPIC_1)
mqtt.subscribe(AWS_SUB_TOPIC_2)
mqtt.subscribe(SHADOW_TOPIC + 'get/accepted')

timer = time.time()
prev_state = -1

# Main loop
while True:
    # Check WiFi connectivity status
    if not wlan.isconnected():
        reconnect()
        
    # Check alarm state, only update display if changed to avoid flickering
    if alarm_state == 1 and prev_state != 1:
        lcd.fillScreen(0xFF0000)
        lcd.setCursor(20,20)
        lcd.print('AWS Badge #{}'.format(BADGE_NO))
        lcd.setCursor(20,200)
        lcd.print('Warning!')
    elif alarm_state == 0 and prev_state != 0:
        lcd.fillScreen(0x00FF00)
        lcd.setCursor(20,20)
        lcd.print('AWS Badge #{}'.format(BADGE_NO))
        lcd.setCursor(20,200)
        lcd.print('Safe')
    
    prev_state = alarm_state
    
    # Check for messages, send messages, check shadow, based on frequency defined above
    if timer + AWS_PUB_FREQ < time.time():
        # Check for messages on subscribed topics
        mqtt.check_msg()
        
        # Publish get shadow message
        mqtt.publish(topic=SHADOW_TOPIC + 'get', msg='', qos=0)
        
        # Publish update to AWS IoT
        message = ujson.dumps({
            "device_id"     : THING_NAME,
            "time_seconds"  : int(time.time() + NTP_TIME_SHIFT),
            "uptime"        : int(time.time() - start_time),
            "alarm_state"   : alarm_state})
        
        try:
            mqtt.publish(topic=AWS_PUB_TOPIC, msg=message, qos=0)
        except:
            pass

        # Publish shadow update
        message = ujson.dumps({
            "state": {
                "reported": {
                    "alarm_state": alarm_state
                    }
                }
            })
        mqtt.publish(topic=SHADOW_TOPIC + 'update', msg=message, qos=0)
        
        timer = time.time()
        
    time.sleep(0.25)
    
    # Reset badge periodically
    if RESET_TIMER * 3600 < time.time() - start_time:
        machine.reset()






