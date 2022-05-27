'''
Handler for chromecast devices, is able to collect devices into rooms, so multiple chromecast
devices can be controlled as one mqtt topic / endpoint.
'''
import re
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
    mqtt: MQTT
    device_count = 0
    device_split_char = '_'

    def __init__(self, mqtt: MQTT, alias: Alias, device_split=False):
        self.__device_split = device_split
        self.mqtt = mqtt
        self.alias = alias

    def discover(self):
        '''
        Start discovering chromecasts on the network.
        '''
        pychromecast.get_chromecasts(callback=self.__search_callback, blocking=False)

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

    def __search_callback(self, chromecast: pychromecast.Chromecast):
        chromecast.connect()
        self.device_count += 1
        name = chromecast.name.lower().replace(' ', self.device_split_char)
        room_name = self.__room(name)
        device = self.__device(name)
        if room_name not in self.rooms:
            self.rooms.update({room_name : RoomState(room_name, self.__device_split)})
            control_path = f'{room_name}/control/+'
            self.mqtt.message_callback_add(control_path, self.__mqtt_action)

        room = self.rooms[room_name]
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

    def __cleanup(self, room):
        self.mqtt.publish(room + '/capabilities', None, retain=False)
        self.mqtt.publish(room + '/media', None, retain=False)
        self.mqtt.publish(room + '/state', None, retain=False)
        self.mqtt.publish(room + '/volume', None, retain=False)
        self.mqtt.publish(room + '/app', None, retain=False)
        self.mqtt.publish(room + '/device', None, retain=False)
