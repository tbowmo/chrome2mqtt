from chrome2mqtt.chromestate import ChromeState

import json
from types import SimpleNamespace as Namespace
from time import sleep

class RoomState:
    __state = None
    __room = 'N/A'
    __active = 'N/A'
    __last_media = None
    __last_state = None
    __state_changed = False
    __media_changed = False
    __devices = {}

    @property
    def room(self): 
        return self.__room

    @property
    def active_device(self):
        return self.__active
    
    @property
    def state(self):
        return self.__state

    @property
    def state_json(self):
        return self.__state.state_json

    @property
    def media_json(self):
        return self.__state.media_json

    @property
    def state_changed(self):
        state = self.__state_changed
        self.__state_changed = False
        return state
    
    @property
    def media_changed(self):
        ''' Returns true if media has changed since last time '''
        state = self.__media_changed
        self.__media_changed = False
        return state
        
    def __init__(self, room):
        self.__room = room

    @state.setter 
    def state(self, newState: ChromeState):
        if self.state is not None and newState.name != self.__active:
            if self.state.app != 'None' and newState.app == 'None':
                return

        self.__state = newState
        self.__active = newState.name
        if self.__last_media != newState.media_json:
            self.__media_changed = True
            self.__last_media = newState.media_json
        if self.__last_state != newState.state_json:
            self.__state_changed = True
            self.__last_state = newState.state_json

    def add_device(self, chromeDevice, name):
        self.__devices.update({name: chromeDevice})
    
    def action(self, command, parameter, allDevices = False):
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
            except:
                pass
        else:
            if allDevices:
                for dev in self.__devices.items():
                    dev.action(command, parameter)
            else:
                self.__devices[self.__active].action(command, parameter)
