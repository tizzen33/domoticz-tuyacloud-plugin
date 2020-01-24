# domoticz-tuyacloud-plugin
This Domoticz plugins creates a connection to the Tuya Cloud, imports devices of type 'switch' and lets you control these devices.
* This is a first draft and works fine for my single device. This will not work for lights or other equipment *

## Prerequisites
- Functioning Domoticz installation
- Python 3 installed on your system
- Python dependencies: requests

## Installation
- Change directory to domoticz/plugins
- git clone https://github.com/tizzen33/domoticz-tuyacloud-plugin.git
- Restart domoticz
- Create new Hardware of type 'Tuya Cloud'
- Fill in your Tuya login details and your mobile country code (e.g. 32 for Belgium)

## Devices
- After enabling the Hardware, the plugin will initialize the connection and will create the devices
- Go to Devices and enable the devices you want

Have fun with it!
