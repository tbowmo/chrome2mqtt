'''
Stores state of a chromedevice in a more MQTT friendly maner.

use ChromeState from this module, to handle the chromecast states.
'''
import json
import abc
from time import time
from attrs import define, field, asdict
from pychromecast.controllers.receiver import CastStatus
from pychromecast.controllers.media import MediaStatus

class BaseHelper(metaclass=abc.ABCMeta):
    ''' Base class, defining methods for jsonifying data '''
    #pylint: disable=missing-docstring
    def json(self):
        return json.dumps(asdict(self))

    @abc.abstractmethod
    def set_cast_state(self, status: CastStatus):
        pass

    @abc.abstractmethod
    def set_media_state(self, media_status: MediaStatus):
        pass

@define
class Media(BaseHelper):
    '''
        Helper class for holding information about the current playing media
    '''
    #pylint: disable=too-many-instance-attributes, missing-docstring
    #All attributes are needed in this object, to hold media info.

    device: str = field()
    title: str = field(init = False, default='')
    artist: str = field(init = False, default='')
    album: str = field(init = False, default='')
    album_art: str = field(init = False, default='')
    metadata_type: str = field(init = False, default=None)
    content_id: str = field(init = False, default=None)
    duration: float = field(init = False, default=None)
    current_time: float = field(init = False, default=None)
    last_update: float = field(init = False, default=None)

    def set_media_state(self, media_status: MediaStatus):
        self.title = media_status.title
        self.artist = media_status.artist
        self.album = media_status.album_name
        self.metadata_type = media_status.metadata_type
        self.duration = media_status.duration
        self.current_time = media_status.current_time
        self.last_update = time()
        if media_status.images:
            images = media_status.images
            self.album_art = images[0].url
        else:
            self.album_art = ''
        self.content_id = media_status.content_id

    def set_cast_state(self, status: CastStatus):
        # Empty as we do not use any info on the CastStatus object
        pass

@define
class SupportedFeatures(BaseHelper):
    '''
        Helper class for holding information about supported features of the current stream / app
    '''
    skip_fwd: bool = field(init = False, default=False)
    skip_bck: bool = field(init = False, default=False)
    pause: bool = field(init = False, default=False)
    volume: bool = field(init = False, default=False)
    mute: bool = field(init = False, default=False)

    def set_media_state(self, media_status: MediaStatus):
        self.skip_fwd = media_status.supports_queue_next or media_status.supports_skip_forward
        self.skip_bck = media_status.supports_queue_prev or media_status.supports_skip_backward
        self.pause = media_status.supports_pause
        self.volume = media_status.supports_stream_volume
        self.mute = media_status.supports_stream_mute

    def set_cast_state(self, status: CastStatus):
        # Empty as we do not use any info on the CastStatus object
        pass

@define
class State(BaseHelper):
    '''
        Helper class holding information about current state of the chromecast
    '''

    device: str = field()
    app: str = field(init = False, default='None')
    state: str = field(init = False, default='STOPPED')
    volume: int = field(init = False, default=0)
    muted: bool = field(init = False, default=False)
    app_icon: str = field(init = False, default='')
    supported_features: SupportedFeatures = field(init = False, default=SupportedFeatures())

    def set_cast_state(self, status: CastStatus):
        self.app = status.display_name or 'None'
        if self.app == 'Backdrop':
            self.app = 'None'
        self.volume = round(status.volume_level * 100)
        self.muted = status.volume_muted == 1
        self.app_icon = status.icon_url
        self.supported_features.set_cast_state(status) #pylint: disable=no-member

    def set_media_state(self, media_status: MediaStatus):
        self.state = media_status.player_state
        self.supported_features.set_media_state(media_status) #pylint: disable=no-member

class ChromeState:
    '''
        Holds state of the chromecast media_status
    '''
    __state = State('')
    __media = Media('')

    def __init__(self, name):
        self.__name = name
        self.clear()

    @property
    def name(self):
        ''' name of the device '''
        return self.__name

    @property
    def app(self):
        ''' which app is currently running '''
        return self.__state.app

    @property
    def state(self):
        ''' what is the current state (playing, stopped, idle, ect) '''
        return self.__state.state

    @property
    def volume(self):
        ''' Volume of the device '''
        if self.__state.muted:
            return 0
        return self.__state.volume

    @property
    def muted(self):
        ''' are we muted? '''
        return self.__state.muted

    @property
    def media_json(self):
        ''' JSON representing the media currently playing '''
        return self.__media.json()

    @property
    def state_json(self):
        ''' JSON representing the current state object (playing, devicename, volume etc.)'''
        return self.__state.json()

    def clear(self):
        ''' Clear all fields '''
        self.__state = State(self.__name)
        self.__media = Media(self.__name)

    def set_cast_state(self, status: CastStatus):
        ''' Update status object '''
        app_name = status.display_name
        if app_name is None or app_name == 'Backdrop' or app_name == '':
            self.clear()
        else:
            self.__media.set_cast_state(status)
            self.__state.set_cast_state(status)

    def set_media_state(self, media_status: MediaStatus):
        ''' Update media object '''
        self.__state.set_media_state(media_status)
        self.__media.set_media_state(media_status)
