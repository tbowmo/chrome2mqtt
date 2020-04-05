''' RoomState is handling the state of a single room with multiple chromecasts
'''
import json
from types import SimpleNamespace as Namespace
from time import sleep
from chrome2mqtt.chromestate import ChromeState

class StateChanged:
    '''Keeps track if state has changed'''
    __last_state = None
    __changed = True

    @property
    def changed(self):
        ''' Returns true if state has changed since last time we called this method '''
        state = self.__changed
        self.__changed = False
        return state

    def update(self, state):
        '''Updates internal state, and check if it is changed from last update'''
        if self.__last_state != state:
            __last_state = state
            __changed = True

class RoomState:
    ''' Handles state of a room, with multiple chromecast devices. '''
    __state = None
    __room = 'N/A'
    __active = 'N/A'
    __state_media = StateChanged()
    __state_state = StateChanged()
    __devices = {}
    __device_split = False

    def __init__(self, room, device_split=False):
        self.__device_split = device_split
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
        return self.__state_state.changed

    @property
    def media_changed(self):
        ''' Returns true if media has changed since last time '''
        return self.__state_media.changed

    @state.setter
    def state(self, new_state: ChromeState):
        ''' Update room state from chromecast devices '''
        if self.state is not None \
           and new_state.name != self.__active \
           and self.state.app != 'None' \
           and new_state.app == 'None':
            return

        self.__state = new_state
        self.__active = new_state.name
        self.__state_media.update(new_state.media_json)
        self.__state_state.update(new_state.state_json)

    def add_device(self, chrome_device, name):
        ''' Add device to this room '''
        self.__devices.update({name: chrome_device})

    def action(self, command, parameter, all_devices=False):
        ''' Room level action, sends the action to the active chromecast '''
        if command == 'play':
            try:
                device = self.__active
                if not self.__device_split:
                    device = self.__determine_playable_device(parameter)
                self.__devices[device].action('play', parameter)
            except ValueError:
                pass
        else:
            if all_devices:
                for dev in self.__devices.items():
                    dev.action(command, parameter)
            else:
                self.__devices[self.__active].action(command, parameter)

    def __determine_playable_device(self, parameter):
        media = json.loads(parameter, object_hook=lambda d: Namespace(**d))
        device = 'tv'
        if hasattr(media, 'type') and media.type.lower().startswith('audio/'):
            device = 'audio'
        if device != self.__active:
            self.__devices[self.__active].action('quit', '')
            sleep(0.5)
        return device
