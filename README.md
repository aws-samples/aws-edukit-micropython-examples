## AWS IoT EduKit MicroPython Examples

## Warning Badge Sample

This is an example of turning the AWS EduKit into a wearable warning badge that communicates with AWS IoT Core. The badge will check it's IoT Shadow to see what state it should be in, based on other sources of information. It will also relay back its current state to both an MQTT topic and update its shadow. The BLE module is activated in Advertising mode so that it can be tracked by other nearby BLE devices for position beaconing.

The sample is currently using the preview version of UIFlow 2.0 firmware, which can be obtained from M5Stack's official updates message board.  Older versions of UIFlow had connectivity issues to AWS that complicated usage.  The preview version does not currently have drivers for many of the features of the EduKit, so we will not be able to use most of the features of the device.

### Prerequisites

  1. Have an AWS account
  2. Create an IoT Thing, generate and down certificates
  3. Create a named shadow for the device
  4. Find your AWS IoT data endpoint from IoT Core Settings
  5. An available 2.4GHz WiFi network, the EduKit does not support 5GHz

### Setting up the IoT EduKit

  1. Connect the EduKit to you computer.
  2. From M5Stack Community, follow the instructions to upload the UIFlow 2.0 firmware to the device [https://community.m5stack.com/topic/4096/uiflow-2-0-2-firmware-preview-version].
  3. Using Thonny or another suitable IDE, connect to the device.
  4. Create a "libs" and "certs" folder on the device.
  5. Copy the certificate (certificate.pem.crt) and private key (private.pem.key) to your "certs" folder.
  6. Copy "ble_advertising.py" to the "libs" folder.
  7. Edit the "main.py" file with the correct device/WiFi information.
  8. Replace the "main.py" on the device with the edited sample.
  9. Restart the device.

### How to interact

  1. Send commands directly to the device over MQTT using the MQTT Test Client:
    - Example topic:      EduKit/WarningBadge/1/down
    - Example messages:   
      a. {"command" : "enter_alarm"}
      b. {"command" : "exit_alarm"}
  2. Update the desired state of the device shadow:
          {"state" : {"desired" : {"alarm_state" : "enter_alarm"}}}
          {"state" : {"desired" : {"alarm_state" : "exit_alarm"}}}


## TODO

Add more samples!

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

