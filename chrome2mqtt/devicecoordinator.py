'''
Handler for chromecast devices, is able to collect devices into rooms, so multiple chromecast
devices can be controlled as one mqtt topic / endpoint.
'''
import re
from os import path
from time import sleep
import pychromecast

from chrome2mqtt.chromeevent import ChromeEvent
from chrome2mqtt.chromestate import ChromeState
from chrome2mqtt.mqtt import MQTT
from chrome2mqtt.roomstate import RoomState

class DeviceCoordinator:
    '''
    Handles chromecasts devices, organizing them into rooms (normal behavior),
    or as standalone devices (devicesplit=true)
    '''
    rooms = {}
    mqtt: MQTT = None
    device_count = 0
    device_split_char = '_'

    def __init__(self, mqtt: MQTT, devicesplit=False):
        self.devicesplit = devicesplit
        self.mqtt = mqtt
        control_path = '+/control/#'
        self.mqtt.message_callback_add(control_path, self.__mqtt_action)

    def discover(self, max_devices=0):
        '''
        Discover chromecast devices on the network.

        If max_devices is specified, discovery is turned off, when the number of
        found devices has been reached
        '''
        stop_discovery = pychromecast.get_chromecasts(callback=self.__search_callback,
                                                      blocking=False)
        while (max_devices > 0 and self.device_count < max_devices):
            sleep(0.5)
        stop_discovery()

    def cleanup(self):
        ''' Clean up MQTT topics for all registered rooms '''
        for room in self.rooms:
            self.__cleanup(room)

    def __mqtt_action(self, client, userdata, message): #pylint: disable=unused-argument
        parameter = message.payload.decode("utf-8")
        command = path.basename(path.normpath(message.topic))
        room = self.rooms[self.__decode_mqtt_topic(message)]
        room.action(command, parameter)

    def __decode_mqtt_topic(self, message):
        '''Get the room name from our own topics'''
        regex = r"{0}(\w*)\/.*".format(self.mqtt.root)
        matches = re.search(regex, message.topic)
        assert matches is not None, 'Can not extract room name from topic "{0}"'.format(message.topic) #pylint: disable=line-too-long
        return matches.group(1)

    def __room(self, device):
        if self.devicesplit:
            return device
        return device.split(self.device_split_char)[1]

    def __device(self, device):
        if self.devicesplit:
            return device
        return device.split(self.device_split_char)[0]

    def __event_handler(self, state: ChromeState, device=None):
        room_name = self.__room(device)
        self.rooms[room_name].state = state

        self.__mqtt_publish(self.rooms[room_name])

    def __search_callback(self, chromecast):
        chromecast.connect()
        self.device_count += 1
        name = chromecast.device.friendly_name.lower().replace(' ', self.device_split_char)
        room_name = self.__room(name)
        device = self.__device(name)
        if room_name not in self.rooms:
            self.rooms.update({room_name : RoomState(room_name)})
        room = self.rooms[room_name]
        room.add_device(ChromeEvent(chromecast,
                                    ChromeState(device),
                                    self.__event_handler,
                                    name),
                        device)

    def __mqtt_publish(self, room: RoomState, force=False):
        base = room.room
        self.mqtt.publish('{0}/device'.format(base), room.active_device, retain=True)
        if (force or room.media_changed):
            self.mqtt.publish('{0}/media'.format(base), room.media_json, retain=True)
        if (force or room.state_changed):
            self.mqtt.publish('{0}/capabilities'.format(base), room.state_json, retain=True)
            self.mqtt.publish('{0}/state'.format(base), room.state.state, retain=True)
            self.mqtt.publish('{0}/volume'.format(base), room.state.volume, retain=True)
            self.mqtt.publish('{0}/app'.format(base), room.state.app, retain=True)

    def __cleanup(self, room):
        self.mqtt.publish(room + '/capabilities', None, retain=False)
        self.mqtt.publish(room + '/media', None, retain=False)
        self.mqtt.publish(room + '/state', None, retain=False)
        self.mqtt.publish(room + '/volume', None, retain=False)
        self.mqtt.publish(room + '/app', None, retain=False)
        self.mqtt.publish(room + '/device', None, retain=False)
