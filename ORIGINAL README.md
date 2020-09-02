# domoticz-tuyacloud-plugin
This Domoticz plugins creates a connection to the Tuya Cloud, imports devices of type 'switch', 'light' or 'cover' and lets you control these devices. 
> This will not work for other equipment

## Prerequisites
- Functioning Domoticz installation
- Python 3 (+ python3-dev) installed on your system
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
- Supported devices: Power Plug (On/Off), Light (On/Off/Set Brightness), Cover (On/Off/Stop)

## What's next
- Feel free to create an issue and post the start-up logs if you have other devices.

Have fun with it!
