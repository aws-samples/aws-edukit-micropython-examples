## AWS IoT EduKit MicroPython Examples

## Warning Badge Sample

This is an example of turning the AWS EduKit into a wearable warning badge that communicates with AWS IoT Core. The badge will check it's IoT Shadow to see what state it should be in, based on other sources of information. It will also relay back its current state to both an MQTT topic and update its shadow. The BLE module is activated in Advertising mode so that it can be tracked by other nearby BLE devices for position beaconing.

### Prerequisites

  1. Have an AWS account
  2. Create an IoT Thing, generate and down certificates
  3. Create a named shadow for the device
  4. Find your AWS IoT data endpoint from IoT Core Settings
  5. An available 2.4GHz WiFi network, the EduKit does not support 5GHz


### How to interact

  1. Send commands directly to the device over MQTT using the MQTT Test Client: 
          Example topic:      EduKit/WarningBadge/1/down
          Example messages:   {"command" : "enter_alarm"}
                              {"command" : "exit_alarm"}
  2. Update the desired state of the device shadow:
          {"state" : {"desired" : {"alarm_state" : "enter_alarm"}}}
          {"state" : {"desired" : {"alarm_state" : "exit_alarm"}}}


## TODO

Add more samples!

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

