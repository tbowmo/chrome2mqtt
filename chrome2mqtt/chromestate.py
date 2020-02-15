import json
from pychromecast.socket_client import CastStatus 
from pychromecast.controllers.media import MediaStatus 
import time

class BaseHelper:
    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    # Dummy method should be implemented in descendants
    def setCastState(self, status: CastStatus):
        pass

    # Dummy method should be implemented in descendants
    def setMediaState(self, media_status: MediaStatus):
        pass

class Media(BaseHelper):
    """
        Helper class for holding information about the current playing media
    """
    def __init__(self, device):
        self.device = device
        self.title = ''
        self.artist = ''
        self.album = ''
        self.album_art = ''
        self.metadata_type = None
        self.content_id = None
        self.duration = None
        self.current_time = None
        self.start_time = None

    def setMediaState(self, media_status: MediaStatus):
        self.title = media_status.title
        self.artist = media_status.artist
        self.album = media_status.album_name
        self.metadata_type = media_status.metadata_type
        self.duration = media_status.duration
        self.current_time = media_status.current_time
        self.start_time = time.time() - self.current_time
        if len(media_status.images) > 0:
            images = media_status.images
            self.album_art = images[0].url
        else:
            self.album_art = ''
        self.content_id = media_status.content_id

class SupportedFeatures(BaseHelper):
    """
        Helper class for holding information about supported features of the current stream / app
    """
    def __init__(self):
        self.skip_fwd = False
        self.skip_bck = False
        self.pause = False
        self.volume = False
        self.mute = False

    def setMediaState(self, media_status: MediaStatus):
        self.skip_fwd = media_status.supports_queue_next or media_status.supports_skip_forward
        self.skip_bck = media_status.supports_queue_prev or media_status.supports_skip_backward
        self.pause = media_status.supports_pause
        self.volume = media_status.supports_stream_volume
        self.mute = media_status.supports_stream_mute

class State(BaseHelper):
    """
        Helper class holding information about current state of the chromecast
    """
    def __init__(self, device):
        self.device = device
        self.app = 'None'
        self.state = 'STOPPED'
        self.volume = 0
        self.muted = False
        self.app_icon = ''
        self.supported_features = SupportedFeatures()
    
    def setCastState(self, status: CastStatus):
        self.app = status.display_name or 'None'
        if self.app == 'Backdrop':
            self.app = 'None'
        self.volume = round(status.volume_level * 100)
        self.muted = status.volume_muted == 1
        self.app_icon = status.icon_url
        self.supported_features.setCastState(status)

    def setMediaState(self, media_status: MediaStatus):
        self.state = media_status.player_state
        self.supported_features.setMediaState(media_status)

class ChromeState:
    """ 
        Holds state of the chromecast media_status 
    """
    __state = State('')
    __media = Media('')

    def __init__(self, name):
        self.__name = name
        self.clear()

    @property
    def name(self):
        return self.__name

    @property
    def app(self):
        return self.__state.app
    
    @property
    def state(self):
        return self.__state.state
    
    @property
    def volume(self):
        if self.__state.muted:
            return 0
        return self.__state.volume

    @property
    def muted(self):
        return self.__state.muted

    @property
    def media_json(self):
        return self.__media.json()

    @property
    def state_json(self):
        return self.__state.json()

    def clear(self):
        """ Clear all fields """
        self.__state = State(self.__name)
        self.__media = Media(self.__name)

    def setCastState(self, status: CastStatus):
        app_name = status.display_name
        if app_name is None or app_name == 'Backdrop' or app_name == '' :
            self.clear()
        else:
            self.__media.setCastState(status)
            self.__state.setCastState(status)

    def setMediaState(self, media_status: MediaStatus):
        self.__state.setMediaState(media_status)
        self.__media.setMediaState(media_status)
