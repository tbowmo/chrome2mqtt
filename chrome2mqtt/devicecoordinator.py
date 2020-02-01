from chrome2mqtt.chromeevent import ChromeEvent
from chrome2mqtt.chromestate import ChromeState
from chrome2mqtt.mqtt import MQTT
from chrome2mqtt.roomstate import RoomState

import pychromecast
import re
from os import path
from time import sleep

class DeviceCoordinator:
    rooms = {}
    mqtt: MQTT = None
    deviceCount = 0

    def __init__(self, mqtt: MQTT, devicesplit = False):
        self.devicesplit = devicesplit
        self.mqtt = mqtt
        controlPath = '+/control/#'
        self.mqtt.subscribe(controlPath)
        self.mqtt.message_callback_add(controlPath, self.__mqttAction)

    def discover(self, maxDevices = 0):
        stop_discovery = pychromecast.get_chromecasts(callback=self.__searchCallback, blocking=False)
        while (maxDevices>0 and self.deviceCount < maxDevices):
            sleep(0.5)
        stop_discovery()

    def cleanup(self):
        for room in self.rooms.keys():
            self.__cleanup(room)

    def __mqttAction(self, client, userdata, message):
        parameter = message.payload.decode("utf-8")
        command = path.basename(path.normpath(message.topic))
        room = self.rooms[self.__decodeMqttTopic(message)]
        room.action(command, parameter)

    def __decodeMqttTopic(self, message):
        '''Get the room name from our own topics'''
        regex = r"{0}(\w*)\/.*".format(self.mqtt.root)
        matches = re.search(regex, message.topic)
        assert matches != None, 'Can not extract room name from topic "{0}"'.format(message.topic)
        return matches.group(1)

    def __room(self, device):
        return device.split('_')[1]

    def __device(self, device):
        return device.split('_')[0]

    def __eventHandler(self, state: ChromeState, device = None):
        roomName = self.__room(device)
        if (self.devicesplit):
            roomName = device
        self.rooms[roomName].state=state

        self.__mqttPublish(self.rooms[roomName])
        pass

    def __searchCallback(self, chromecast):
        chromecast.connect()
        self.deviceCount += 1
        name = chromecast.device.friendly_name.lower().replace(' ', '_')
        roomName = self.__room(name)
        if (self.devicesplit):
            roomName = name
        device = self.__device(name)
        if (roomName not in self.rooms):
            self.rooms.update({roomName : RoomState(roomName)})
        room = self.rooms[roomName]
        room.add_device(ChromeEvent(chromecast, ChromeState(device), self.__eventHandler, name), device)

    def __mqttPublish(self, room: RoomState, force = False):
        base = room.room
        self.mqtt.publish('{0}/device'.format(base), room.active_device, retain=True)
        if (force or room.media_changed):
            self.mqtt.publish('{0}/media'.format(base), room.media_json, retain = True )
        if (force or room.state_changed):
            self.mqtt.publish('{0}/capabilities'.format(base), room.state_json, retain = True )
            self.mqtt.publish('{0}/state'.format(base), room.state.state, retain = True )
            self.mqtt.publish('{0}/volume'.format(base), room.state.volume, retain = True )
            self.mqtt.publish('{0}/app'.format(base), room.state.app, retain=True)

    def __cleanup(self, room):
        self.mqtt.publish(room + '/capabilities', None, retain=False)
        self.mqtt.publish(room + '/media', None, retain=False)
        self.mqtt.publish(room + '/state', None, retain=False)
        self.mqtt.publish(room + '/volume', None, retain=False)
        self.mqtt.publish(room + '/app', None, retain=False)
        self.mqtt.publish(room + '/device', None, retain=False)
    