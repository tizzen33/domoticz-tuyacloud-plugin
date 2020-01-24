"""
<plugin key="tuyacloud" name="Tuya Cloud" author="tizzen33" version="1.0.0" wikilink="http://www.github.com/tizzen33/domoticz-tuyacloud">
    <description>
        <h2>Tuya Cloud plugin</h2><br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>This plugin gets all devices available in your Tuya app</li>
            <li>If you are using a rebranded app like 'LSC Smart Connect', remove your devices and add them again in the Tuya app.</li>
            <li>Login with your e-mail address, password and country code (e.g. 32 for Belgium)</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>At the moment, only power plugs can be discovered and used.</li>
        </ul>
    </description>
    <params>
        <param field="Username" label="Username" width="200px" required="true" default=""/>
        <param field="Password" label="Password" width="30px" required="true" default="" password="true"/>
        <param field="Mode1" label="countryCode" width="150px" required="true"/>
        <param field="Mode2" label="Debug" width="75px">
            <options>
                <option label="Verbose" value="Verbose"/>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import requests
import json
import time

base_url = "https://px1.tuyaeu.com/{}"


class BasePlugin:
    accessDetails = {}
    devices = {}
    device_types = {'switch': {'type': 'Switch','image': 1}}

    def onStart(self):
        self.debugging = Parameters["Mode2"]

        if self.debugging == "Verbose":
            Domoticz.Debugging(2 + 4 + 8 + 16 + 64)
        if self.debugging == "Debug":
            Domoticz.Debugging(2)
        Domoticz.Heartbeat(30)
        Domoticz.Debug('onStart called')

        self.userName = Parameters["Username"].strip()
        self.password = Parameters["Password"].strip()
        self.countryCode = Parameters["Mode1"].strip()

        self.accessDetails = self.connectTuya(self.userName, self.password, self.countryCode)
        
        self.syncDevices()
        
        Domoticz.Debug('Tuya Cloud devices initialized.')
        
    def connectTuya(self, userName, password, countryCode):
        Domoticz.Debug('Starting connection to Tuya Cloud')
        params = {'userName': userName,'password': password,'countryCode': countryCode,'bizType': '','from': 'tuya'}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(base_url.format("homeassistant/auth.do"),headers=headers,params=params)
        response_json = response.json()
        
        if response_json.get('responseStatus') == 'error':
          Domoticz.Debug('Connection error.')
          onStop()
        else:
          Domoticz.Debug('Connection established.')
          return response_json

    def syncDevices(self):
        Domoticz.Debug('Getting devices ...')
        headers = {'Content-Type': 'application/json'}
        header = {'name': 'Discovery', 'namespace': 'discovery', 'payloadVersion': 1}
        payload = {'accessToken': self.accessDetails.get('access_token')}
        data = {'header': header,'payload': payload}
        response = requests.post(base_url.format("homeassistant/skill"),json=data)
        response_json = response.json()
        if response_json and response_json["header"]["code"] == "SUCCESS":
            tuya_devices = response_json["payload"]["devices"]
            Domoticz.Debug('Devices found:{devices}'.format(devices=json.dumps(tuya_devices)))
            for tuya_device in tuya_devices:
                createDomoticzDevice = True
                maxUnit = 1
                Domoticz.Debug('Looping through tuya devices')
                if (Devices):
                    for Device in Devices:
                            Domoticz.Debug('Looping through Domoticz Devices')
                            if (Devices[Device].Unit > maxUnit): maxUnit = Devices[Device].Unit
                            if (Devices[Device].DeviceID.find(tuya_device["id"]) >= 0):
                                createDomoticzDevice = False
                                Domoticz.Debug('Device with identifier {id} already exists.'.format(id=tuya_device["id"]))
                                break
                if (createDomoticzDevice):
                    Domoticz.Device(Name=tuya_device["name"],Unit=maxUnit+1,TypeName=self.device_types[tuya_device["ha_type"]]["type"],Image=self.device_types[tuya_device["ha_type"]]["image"],DeviceID=tuya_device["id"]).Create()
                    Domoticz.Debug('Creating a {type} device with identifier {id}'.format(type=tuya_device["ha_type"],id=tuya_device["id"]))
        else:
            Domoticz.Debug('Device synchronization failed')
        
    def checkAccessToken(self):
        accessToken = self.accessDetails.get('access_token')
        refreshToken = self.accessDetails.get('refresh_token')
        expireTime = int(time.time()) + self.accessDetails.get('expires_in')
        
        if expireTime <= 86400 + int(time.time()):
            data = "grant_type=refresh_token&refresh_token="+refreshToken
            response = requests.get(
                (base_url.format("homeassistant/access.do"))
                + "?" + data)
            response_json = response.json()
            if response_json.get('responseStatus') == 'error':
                Domoticz.Debug('Failed to refresh token')
            else:
                self.accessDetails.update({
                'accessToken': response_json.get('access_token'),
                'refreshToken': response_json.get('refresh_token'),
                'expireTime': int(time.time()) + response_json.get('expires_in')})
                Domoticz.Debug('Access token refreshed')
        #else:
            #Domoticz.Debug('Access token still valid for {expTime}'.format(expTime=self.accessDetails.get('expires_in')))
    
    def updateDevices(self):
        headers = {'Content-Type': 'application/json'}
        header = {'name': 'QueryDevice', 'namespace': 'query', 'payloadVersion': 1}
        payload = {'accessToken': self.accessDetails.get('access_token')}
        for Unit in Devices:
            payload["devId"] = Devices[Unit].DeviceID
            data = {'header': header,'payload': payload}
            response = requests.post(base_url.format("homeassistant/skill"),json=data)
            response_json = response.json()
            if response_json and response_json["header"]["code"] != "SUCCESS":
                Domoticz.Debug('Device status update failed')
            else:
                if(response_json["payload"]["data"]["state"]):
                    Devices[Unit].Update(nValue = 1, str(1))
                else:
                    Devices[Unit].Update(nValue = 0, str(0))
                Domoticz.Debug('Device ' + Devices[Device].Name + ' status updated to ' + str(response_json["payload"]["data"]["state"]))
            
    def onStop(self):
        Domoticz.Debug("onStop called")

    def onCommand(self, Unit, Command, Level, Color):
        commands = {'On': {'comm': 'turnOnOff', 'value': 1}, 'Off': {'comm': 'turnOnOff', 'value': 0}}
        headers = {'Content-Type': 'application/json'}
        header = {'name': commands[Command]["comm"], 'namespace': 'control', 'payloadVersion': 1}
        payload = {'accessToken': self.accessDetails.get('access_token'), 'devId': Devices[Unit].DeviceID, 'value': commands[Command]["value"]}
        data = {'header': header,'payload': payload}
        response = requests.post(base_url.format("homeassistant/skill"),json=data)
        response_json = response.json()
        if response_json['header']['code'] == 'SUCCESS':
            Domoticz.Debug("onCommand: " + Command + ", level (" + str(Level) + ") Color:" + Color)
            Devices[Unit].Update(nValue = commands[Command]["value"], sValue = str(commands[Command]["value"]))
        else:
            Domoticz.Debug("Command failed: " + commands[Command]["comm"] + ", value: " + commands[Command]["value"])

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onDisconnect(self, Connection):
        Domoticz.Debug("Disconnect called")
        
    def onMessage(self, Connection, Data):
        Domoticz.Debug('Incoming message!' + str(Data))

    def onHeartbeat(self):
        self.checkAccessToken()
        self.updateDevices()
        

global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onMessage(Connection, Data):
    global _plugin
    Domoticz.Debug('Message from base')
    _plugin.onMessage(Connection, Data)


def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
