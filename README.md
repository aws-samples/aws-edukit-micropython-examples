## AWS IoT EduKit MicroPython Examples

## Warning Badge Example
This is an example of turning the AWS EduKit into a wearable warning badge that communicates with AWS IoT Core. The badge will check it's IoT Shadow to see what state it should be in, which can be updated by other AWS services, like IoT Events. It will also relay back its current state over an MQTT topic and will update its shadow. The BLE module is enabled in Advertising mode, so that it can be tracked by other nearby BLE devices for possible position beaconing.

### Note
The sample is currently using the preview version of UIFlow 2.0 firmware, which can be obtained from M5Stack's official updates message board.  Older versions of UIFlow had connectivity issues to AWS that complicated usage.  The preview version does not currently have drivers for many of the features of the EduKit, so we will not be able to use most of the features of the device.

### Prerequisites
  1. Have an AWS account
  1. Create an IoT Thing, generate and down certificates
  1. Create a named shadow for the device
  1. Find your AWS IoT data endpoint from IoT Core Settings
  1. An available 2.4GHz WiFi network, the EduKit does not support 5GHz

### Setting up the IoT EduKit
  1. Connect the EduKit to you computer.
  1. From M5Stack Community, follow the instructions to upload the UIFlow 2.0 firmware to the device [https://community.m5stack.com/topic/4096/uiflow-2-0-2-firmware-preview-version].
  1. Using Thonny or another suitable IDE, connect to the device.
  1. Create a **libs** and **certs** folder on the device.
  1. Copy the certificate (certificate.pem.crt) and private key (private.pem.key) to your **certs** folder.
  1. Copy **ble_advertising.py** to the **libs** folder.
  1. Edit the **main.py** file with the correct device/WiFi information.
  1. Replace the **main.py** on the device with the edited sample.
  1. Restart the device.

### How to interact
Send commands directly to the device over MQTT using the MQTT Test Client:
  - Example topic: EduKit/WarningBadge/1/down 
  - Example messages: 
  - - {"command" : "enter_alarm"} 
  - - {"command" : "exit_alarm"} 

Update the desired state of the device shadow:
  - {"state" : {"desired" : {"alarm_state" : "enter_alarm"}}}
  - {"state" : {"desired" : {"alarm_state" : "exit_alarm"}}}


## TODO

Add more samples!

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

