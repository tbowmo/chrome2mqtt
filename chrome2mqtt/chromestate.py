import json
import logging
from pychromecast.socket_client import CastStatus 
from pychromecast.controllers.media import MediaStatus 

class ChromeState:
    """ 
        Holds state of the chromecast mediaStatus 
    """
    __device_type = ''
    __chrome_app = ''
    __title = ''
    __artist = ''
    __album = ''
    __supports_skip_fwd = False
    __supports_skip_bck = False
    __supports_pause = False
    __state = ''
    __supports_volume = False
    __supports_mute = False
    __volume = 0
    __muted = False
    __app_icon = ''
    __album_art = ''

    @property
    def app(self):
        return self.__chrome_app
    
    @property
    def state(self):
        return self.__state
    
    @property
    def volume(self):
        if (self.__muted):
            return 0
        return self.__volume

    @property
    def muted(self):
        return self.__muted

    def __init__(self, device):
        if device.cast_type == 'cast':
            self.__device_type = 'video'
        else:
            self.__device_type = device.cast_type
        self.clear()
        self.log = logging.getLogger('chromestate_' + device.cast_type)

    @property
    def media(self):
        media_dict = {
            'title': self.__title,
            'artist': self.__artist,
            'album': self.__album,
            'album_art': self.__album_art,
        }
        return json.dumps(media_dict).encode('utf-8')

    @property
    def capabilities(self):
        supports = {
            'skip_fwd': self.__supports_skip_fwd,
            'skip_bck': self.__supports_skip_bck,
            'pause': self.__supports_pause,
            'volume': self.__supports_volume,
            'mute': self.__supports_mute
        }

        capabilities = {
            'state': self.__state,
            'volume': self.__volume,
            'muted': self.__muted,
            'app': self.__chrome_app,
            'app_icon': self.__app_icon,
            'supported_features': supports
        }
        return json.dumps(capabilities).encode('utf-8')

    def clear(self):
        """ Clear all fields """
        self.__state = "STOPPED"
        self.__chrome_app = "None"
        self.__title = ''
        self.__artist = ''
        self.__album = ''
        self.__pause = False
        self.__skip_fwd = False
        self.__skip_bck = False
        self.__volume = False
        self.__volume = 0
        self.__album_art = ''
        self.__app_icon = ''

    def setState(self, status: CastStatus):
        app_name = status.display_name
        if app_name is None or app_name == 'Backdrop' or app_name == '' :
            self.clear()
        else:
            self.__chrome_app = app_name
        self.__volume = round(status.volume_level * 100)
        self.__muted = False
        if (status.volume_muted == 1):
            self.__muted = True
        self.__app_icon = status.icon_url

    def setMedia(self, mediaStatus: MediaStatus):
        if hasattr(mediaStatus, 'player_state') and mediaStatus.player_state is not None:
            self.__state = mediaStatus.player_state

        if hasattr(mediaStatus, 'images'):
            images = mediaStatus.images
            self.__album_art = images[0].url
        else:
            self.__album_art = ''

        if hasattr(mediaStatus, 'supports_pause'):
            self.__supports_pause = mediaStatus.supports_pause
        else:
            self.__supports_pause = False

        if hasattr(mediaStatus, 'supports_skip_forward'):
            self.__supports_skip_fwd = mediaStatus.supports_skip_forward
        else:
            self.__supports_skip_fwd = False

        if hasattr(mediaStatus, 'supports_skip_backward'):
            self.__supports_skip_bck = mediaStatus.supports_skip_backward
        else:
            self.__supports_skip_bck = False

        if hasattr(mediaStatus, 'supports_stream_volume'):
            self.__supports_volume = mediaStatus.supports_stream_volume
        else:
            self.__supports_volume = False

        if hasattr(mediaStatus, 'supports_stream_mute'):
            self.__supports_mute = mediaStatus.supports_stream_mute
        else:
            self.__supports_mute = False

        if hasattr(mediaStatus, 'title'):
            self.__title = mediaStatus.title

        if hasattr(mediaStatus, 'artist'):
            self.__artist = mediaStatus.artist

        if hasattr(mediaStatus, 'album_name'):
            self.__album = mediaStatus.album_name
