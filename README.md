# domoticz-tuyacloud-plugin
This Domoticz plugins creates a connection to the Tuya Cloud, imports devices of type 'switch' or 'light' and lets you control these devices. 
> This will not work for other equipment

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
- Supported devices: Power Plug (On/Off), Light (On/Off)

## What's next
- A smoke detector is in transit. Once I receive it, I will update the plugin to make it work with this device.
- Feel free to create an issue and post the start-up logs if you have another type of device.

Have fun with it!
