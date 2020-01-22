"""
<plugin key="tuyacloud" name="Tuya Cloud" author="tizzen" version="1.0.0" wikilink="http://www.github.com/tizzen33/domoticz-tuyacloud" externallink="http://www.github.com/tizzen33/domoticz-tuyacloud">
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

    def onStart(self):
        self.debugging = Parameters["Mode2"]

        if self.debugging == "Verbose":
            Domoticz.Debugging(2 + 4 + 8 + 16 + 64)
        if self.debugging == "Debug":
            Domoticz.Debugging(2)

        Domoticz.Debug("onStart called")

        self.userName = Parameters["Username"].strip()
        self.password = Parameters["Password"].strip()
        self.countryCode = Parameters["Mode1"].strip()

        self.accessDetails = self.connectTuya(self.userName, self.password, self.countryCode)
        
        #self.accessDetails = self.checkAccessToken()
        
        self.syncDevices(self.accessDetails.get('access_token'))
        
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

    def syncDevices(self, accessToken):
        Domoticz.Debug('Getting devices ...')
        headers = {'Content-Type': 'application/json'}
        header = {'name': 'Discovery', 'namespace': 'discovery', 'payloadVersion': 1}
        payload = {'accessToken': accessToken}
        data = {'header': header,'payload': payload}
        response = requests.post(base_url.format("homeassistant/skill"),json=data)
        response_json = response.json()
        Domoticz.Debug('Devices found:{devices}'.format(devices=json.dumps(response_json)))   
        
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
        else:
            Domoticz.Debug('Access token still valid for {expTime}'.format(expTime=self.accessDetails.get('expires_in')))
    
    def onStop(self):
        Domoticz.Debug("onStop called")

    def onCommand(self, Unit, Command, Level, Color):
        Domoticz.Debug("onCommand: " + Command + ", level (" + str(Level) + ") Color:" + Color)

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onDisconnect(self, Connection):
        Domoticz.Debug("Disconnect called")
        
    def onMessage(self, Connection, Data):
        Domoticz.Debug('Incoming message!' + str(Data))

    def onHeartbeat(self):
        Domoticz.Debug("Heartbeating...")
        self.checkAccessToken()
        

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
