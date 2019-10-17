import json
import logging
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
    def __init__(self, title='', artist='', album='', album_art=''):
        self.title = title
        self.artist = artist
        self.album = album
        self.album_art = album_art

    def setMediaState(self, mediaStatus: MediaStatus):
        self.title = mediaStatus.title
        self.artist = mediaStatus.artist
        self.album = mediaStatus.album_name
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
        self.skip_fwd = mediaStatus.supports_skip_forward
        self.skip_bck = mediaStatus.supports_skip_backward
        self.pause = mediaStatus.supports_pause
        self.volume = mediaStatus.supports_stream_volume
        self.mute = mediaStatus.supports_stream_mute
   

class Capabilities(BaseHelper):
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
        Holds state of the chromecast __mediaStatus 
    """
    __capabilities = Capabilities()
    __media = Media()

    def __init__(self, device):
        self.clear()
        self.log = logging.getLogger('chromestate_' + device.cast_type)
        self.__media = Media()
        self.__capabilities = Capabilities()

    @property
    def app(self):
        return self.__capabilities.app
    
    @property
    def state(self):
        return self.__capabilities.state
    
    @property
    def volume(self):
        if self.__capabilities.muted:
            return 0
        return self.__capabilities.volume

    @property
    def muted(self):
        return self.__capabilities.muted

    @property
    def media(self):
        return self.__media.json()

    @property
    def capabilities(self):
        return self.__capabilities.json()

    def clear(self):
        """ Clear all fields """
        self.__capabilities = Capabilities()
        self.__media = Media()

    def setCastState(self, status: CastStatus):
        app_name = status.display_name
        if app_name is None or app_name == 'Backdrop' or app_name == '' :
            self.clear()
        else:
            self.__media.setCastState(status)
            self.__capabilities.setCastState(status)

    def setMediaState(self, mediaStatus: MediaStatus):
        self.__capabilities.setMediaState(mediaStatus)
        self.__media.setMediaState(mediaStatus)
