import json
from pychromecast.socket_client import CastStatus 
from pychromecast.controllers.media import MediaStatus 

class BaseHelper:
    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def setCastState(self, status: CastStatus):
        pass

    def setMediaState(self, mediaStatus: MediaStatus):
        pass

class Media(BaseHelper):
    """
        Helper class for holding information about the current playing media
    """
    def __init__(self):
        self.title = ''
        self.artist = ''
        self.album = ''
        self.album_art = ''
        self.metadata_type = None

    def setMediaState(self, mediaStatus: MediaStatus):
        self.title = mediaStatus.title
        self.artist = mediaStatus.artist
        self.album = mediaStatus.album_name
        self.metadata_type = mediaStatus.metadata_type
        if len(mediaStatus.images) > 0:
            images = mediaStatus.images
            self.album_art = images[0].url
        else:
            self.album_art = ''

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

    def setMediaState(self, mediaStatus: MediaStatus):
        self.skip_fwd = mediaStatus.supports_queue_next or mediaStatus.supports_skip_forward
        self.skip_bck = mediaStatus.supports_queue_prev or mediaStatus.supports_skip_backward
        self.pause = mediaStatus.supports_pause
        self.volume = mediaStatus.supports_stream_volume
        self.mute = mediaStatus.supports_stream_mute

class State(BaseHelper):
    """
        Helper class holding information about current state of the chromecast
    """
    def __init__(self):
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

    def setMediaState(self, mediaStatus: MediaStatus):
        self.state = mediaStatus.player_state
        self.supported_features.setMediaState(mediaStatus)

class ChromeState:
    """ 
        Holds state of the chromecast mediaStatus 
    """
    __state = State()
    __media = Media()

    def __init__(self, device):
        self.clear()

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
        self.__state = State()
        self.__media = Media()

    def setCastState(self, status: CastStatus):
        app_name = status.display_name
        if app_name is None or app_name == 'Backdrop' or app_name == '' :
            self.clear()
        else:
            self.__media.setCastState(status)
            self.__state.setCastState(status)

    def setMediaState(self, mediaStatus: MediaStatus):
        self.__state.setMediaState(mediaStatus)
        self.__media.setMediaState(mediaStatus)
