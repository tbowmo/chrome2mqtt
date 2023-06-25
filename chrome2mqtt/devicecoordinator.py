'''
Handler for chromecast devices, is able to collect devices into rooms, so multiple chromecast
devices can be controlled as one mqtt topic / endpoint.
'''
import re
from typing import Dict
import pychromecast
from attrs import define, field
from .chromeevent import ChromeEvent
from .chromestate import ChromeState
from .mqtt import MQTT
from .roomstate import RoomState
from .alias import Alias

@define
class DeviceCoordinator:
    '''
    Handles chromecast devices, organizing them into rooms (normal behavior),
    or as standalone devices (device_split=true)
    '''
    #pylint: disable=no-member

    mqtt: MQTT = field()
    alias: Alias = field()
    device_split = field(default=False)
    __rooms: Dict[str, RoomState] = field(init= False, default={})
    __device_split_char = field(init=False, default='_')

    def discover(self):
        '''
        Start discovering chromecasts on the network.
        '''
        pychromecast.get_chromecasts(callback=self.__search_callback, blocking=False)

    def cleanup(self):
        ''' Clean up MQTT topics for all registered rooms '''
        for room in self.__rooms:
            self.__cleanup(room)

    def __mqtt_action(self, client, userdata, message): #pylint: disable=unused-argument
        parameter = message.payload.decode("utf-8")
        command = self.__decode_mqtt_command(message)
        room = self.__rooms[self.__decode_mqtt_room(message)]
        room.action(command, parameter)

    def __decode_mqtt_command(self, message):
        '''Get the command that was sent in the topic'''
        regex = r"\/control\/(.+)"
        matches = re.search(regex, message.topic)
        assert matches is not None, f'Can not extract command from topic "{message.topic}"'
        return matches.group(1)

    def __decode_mqtt_room(self, message):
        '''Get the room name from our own topics'''
        regex = rf"{self.mqtt.root}(.+)\/control\/.*"
        matches = re.search(regex, message.topic)
        assert matches is not None, f'Can not extract room name from topic "{message.topic}"' #pylint: disable=line-too-long
        return matches.group(1)

    def __room(self, device):
        room = device
        if not self.device_split:
            room = device.split(self.__device_split_char)[0]
        return self.alias.get(room)

    def __device(self, device):
        if self.device_split:
            return device
        return device.split(self.__device_split_char)[1]

    def __event_handler(self, state: ChromeState, device=None):
        room_name = self.__room(device)
        self.__rooms[room_name].state = state

        self.__mqtt_publish(self.__rooms[room_name])

    def __search_callback(self, chromecast: pychromecast.Chromecast):
        chromecast.connect()
        name = chromecast.name.lower().replace(' ', self.__device_split_char)
        room_name = self.__room(name)
        device = self.__device(name)
        if room_name not in self.__rooms:
            self.__rooms.update({room_name : RoomState(room_name, self.device_split)})
            control_path = f'{room_name}/control/+'
            self.mqtt.message_callback_add(control_path, self.__mqtt_action)

        room = self.__rooms[room_name]
        room.add_device(ChromeEvent(chromecast,
                                    ChromeState(device),
                                    self.__event_handler,
                                    name),
                        device)

    def __mqtt_publish(self, room: RoomState, force=False):
        base = room.room
        self.mqtt.publish(f'{base}/device', room.active_device, retain=True)
        if (force or room.media_changed):
            self.mqtt.publish(f'{base}/media', room.media_json, retain=True)
        if (force or room.state_changed):
            self.mqtt.publish(f'{base}/capabilities', room.state_json, retain=True)
            self.mqtt.publish(f'{base}/state', room.state.state, retain=True)
            self.mqtt.publish(f'{base}/volume', room.state.volume, retain=True)
            self.mqtt.publish(f'{base}/app', room.state.app, retain=True)

    def __cleanup(self, room: str):
        self.mqtt.publish(f'{room}/capabilities', None, retain=False)
        self.mqtt.publish(f'{room}/media', None, retain=False)
        self.mqtt.publish(f'{room}/state', None, retain=False)
        self.mqtt.publish(f'{room}/volume', None, retain=False)
        self.mqtt.publish(f'{room}/app', None, retain=False)
        self.mqtt.publish(f'{room}/device', None, retain=False)
