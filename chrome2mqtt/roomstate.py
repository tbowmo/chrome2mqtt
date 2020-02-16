''' RoomState is handling the state of a single room with multiple chromecasts
'''
import json
from types import SimpleNamespace as Namespace
from time import sleep
from chrome2mqtt.chromestate import ChromeState

class RoomState:
    ''' Handles state of a room, with multiple chromecast devices. '''
    __state = None
    __room = 'N/A'
    __active = 'N/A'
    __last_media = None
    __last_state = None
    __state_changed = False
    __media_changed = False
    __devices = {}

    def __init__(self, room):
        self.__room = room

    @property
    def room(self):
        ''' name of the room '''
        return self.__room

    @property
    def active_device(self):
        ''' Name of the device that is active '''
        return self.__active

    @property
    def state(self):
        ''' state of the active device '''
        return self.__state

    @property
    def state_json(self):
        ''' JSON representation of the state object from the currently active device'''
        return self.__state.state_json

    @property
    def media_json(self):
        ''' JSON representation of the media of the currently active device in the room '''
        return self.__state.media_json

    @property
    def state_changed(self):
        ''' Returns true if state has changed since last time this was called '''
        state = self.__state_changed
        self.__state_changed = False
        return state

    @property
    def media_changed(self):
        ''' Returns true if media has changed since last time '''
        state = self.__media_changed
        self.__media_changed = False
        return state

    @state.setter
    def state(self, new_state: ChromeState):
        ''' Update room state from chromecast devices '''
        if self.state is not None and new_state.name != self.__active:
            if self.state.app != 'None' and new_state.app == 'None':
                return

        self.__state = new_state
        self.__active = new_state.name
        if self.__last_media != new_state.media_json:
            self.__media_changed = True
            self.__last_media = new_state.media_json
        if self.__last_state != new_state.state_json:
            self.__state_changed = True
            self.__last_state = new_state.state_json

    def add_device(self, chrome_device, name):
        ''' Add device to this room '''
        self.__devices.update({name: chrome_device})

    def action(self, command, parameter, all_devices=False):
        ''' Room level action, sends the action to the active chromecast '''
        if command == 'play':
            try:
                media = json.loads(parameter, object_hook=lambda d: Namespace(**d))
                device = 'tv'
                if hasattr(media, 'type') and media.type.lower().startswith('audio/'):
                    device = 'audio'
                if device != self.__active:
                    self.__devices[self.__active].action('quit', '')
                    sleep(0.5)
                self.__devices[device].action('play', parameter)
            except ValueError:
                pass
        else:
            if all_devices:
                for dev in self.__devices.items():
                    dev.action(command, parameter)
            else:
                self.__devices[self.__active].action(command, parameter)
