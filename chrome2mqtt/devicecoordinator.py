'''
Handler for chromecast devices, is able to collect devices into rooms, so multiple chromecast
devices can be controlled as one mqtt topic / endpoint.
'''
import re
from time import sleep
import pychromecast

from chrome2mqtt.chromeevent import ChromeEvent
from chrome2mqtt.chromestate import ChromeState
from chrome2mqtt.mqtt import MQTT
from chrome2mqtt.roomstate import RoomState
from chrome2mqtt.alias import Alias

class DeviceCoordinator:
    '''
    Handles chromecasts devices, organizing them into rooms (normal behavior),
    or as standalone devices (device_split=true)
    '''
    rooms = {}
    mqtt: MQTT = None
    device_count = 0
    device_split_char = '_'

    def __init__(self, mqtt: MQTT, alias: Alias, device_split=False):
        self.__device_split = device_split
        self.mqtt = mqtt
        self.alias = alias

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
        command = self.__decode_mqtt_command(message)
        room = self.rooms[self.__decode_mqtt_room(message)]
        room.action(command, parameter)

    def __decode_mqtt_command(self, message): #pylint: disable=no-self-use
        '''Get the command that was sent in the topic'''
        regex = r"\/control\/(.+)"
        matches = re.search(regex, message.topic)
        assert matches is not None, 'Can not extract command from topic "{0}"'.format(message.topic)
        return matches.group(1)

    def __decode_mqtt_room(self, message):
        '''Get the room name from our own topics'''
        regex = r"{0}(.+)\/control\/.*".format(self.mqtt.root)
        matches = re.search(regex, message.topic)
        assert matches is not None, 'Can not extract room name from topic "{0}"'.format(message.topic) #pylint: disable=line-too-long
        return matches.group(1)

    def __room(self, device):
        room = device
        if not self.__device_split:
            room = device.split(self.device_split_char)[0]
        return self.alias.get(room)

    def __device(self, device):
        if self.__device_split:
            return device
        return device.split(self.device_split_char)[1]

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
            self.rooms.update({room_name : RoomState(room_name, self.__device_split)})
            control_path = '{0}/control/#'.format(room_name)
            self.mqtt.message_callback_add(control_path, self.__mqtt_action)

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
