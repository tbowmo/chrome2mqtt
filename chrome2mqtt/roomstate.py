''' RoomState is handling the state of a single room with multiple chromecasts
'''
import json
from logging import getLogger, Logger
from types import SimpleNamespace as Namespace
from time import sleep
from attrs import define, field
from .chromestate import ChromeState

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
            self.__last_state = state
            self.__changed = True

@define
class RoomState:
    ''' Handles state of a room, with multiple chromecast devices. '''
    #pylint: disable=no-member, too-many-instance-attributes
    room: str = field()
    device_split: bool = field(default = False)
    __state: ChromeState = field(init = False, default=None)
    __active:str = field(init=False, default='N/A')
    __state_media: StateChanged = field(init=False, default=StateChanged())
    __state_state: StateChanged = field(init=False, default=StateChanged())
    __devices: dict = field(init=False, default={})
    __log: Logger = field(init=False)

    def __attrs_post_init__(self):
        self.__log = getLogger(f'roomState_{self.room}')

    @property
    def active_device(self):
        ''' Name of the device that is active '''
        return self.__active

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

    @property
    def state(self):
        ''' state of the active device '''
        return self.__state

    @state.setter
    def state(self, new_state: ChromeState):
        ''' Update room state from chromecast devices '''
        ignored_apps = new_state.app in ('Default Media Receiver', 'None')
        if self.__state is not None \
           and self.__state.app != 'None' \
           and new_state.name != self.__active \
           and ignored_apps:
            return

        if self.__active != new_state.name \
           and self.__active != 'N/A' \
           and self.__state.app != 'None':
            self.__log.info('quit %s', self.__active)
            self.__devices[self.__active].action('quit', '')

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
                if not self.device_split:
                    device = self.__determine_playable_device(parameter)
                self.__devices[device].action('play', parameter)
            except ValueError:
                self.__devices[self.__active].action(command, parameter)
        else:
            if all_devices:
                for dev in self.__devices.items():
                    dev.action(command, parameter)
            else:
                self.__devices[self.__active].action(command, parameter)

    def __determine_playable_device(self, parameter):
        media = json.loads(parameter, object_hook=lambda d: Namespace(**d))
        device = 'tv'
        if hasattr(media, 'type') and media.type.lower().startswith('audio'):
            device = 'audio'
        if device != self.__active:
            self.__devices[self.__active].action('quit', '')
            sleep(0.5)
        return device
