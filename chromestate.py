"""
    holds current state of the chromedevice
"""
import json
import logging
from pychromecast.socket_client import CastStatus 
from pychromecast.controllers.media import MediaStatus 

class ChromeState:
    """ Holds state of the chromecast mediaStatus """
    __device_type = ""
    __chrome_app = ""
    __title = ""
    __artist = ""
    __album = ""
    __skip_fwd = False
    __skip_bck = False
    __pause = False
    __player_state = ""
    __volume = False
    __volume_level = 0
    __volume_level1 = 0

    @property
    def app(self):
        return self.__chrome_app
    
    @property
    def player_state(self):
        return self.__player_state
    
    @property
    def volume_level(self):
        return self.__volume_level

    @property
    def volume_level1(self):
        return self.__volume_level1

    def __init__(self, device):
        if device.cast_type == 'cast':
            self.__device_type = 'video'
        else:
            self.__device_type = device.cast_type
        self.log = logging.getLogger('chromestate_' + device.cast_type)

    @property
    def media(self):
        media_dict = {
            "title": self.__title,
            "artist":self.__artist,
            "album":self.__album,
        }
        return json.dumps(media_dict).encode('utf-8')

    @property
    def state(self):
        state_dict = {
            "skip_fwd": self.__skip_fwd,
            "skip_bck": self.__skip_bck,
            "pause": self.__pause,
            "player_state": self.__player_state,
            "volume": self.__volume,
            "volume_level": self.__volume_level,
            "volume_level1": self.__volume_level1,
            "chrome_app": self.__chrome_app
        }
        return json.dumps(state_dict).encode('utf-8')

    def clear(self):
        """ Clear all fields """
        self.__player_state = "STOPPED"
        self.__chrome_app = ""
        self.__title = ""
        self.__artist = ""
        self.__album = ""
        self.__pause = False
        self.__skip_fwd = False
        self.__skip_bck = False
        self.__volume = False
        self.__volume_level = 0
        self.__volume_level1 = 0


    def setState(self, status: CastStatus):
        app_name = status.display_name
        if app_name is None or app_name == "Backdrop" or app_name == "" :
            self.clear()
            app_name = "None"
        self.__chrome_app = app_name
        self.__volume_level1 = status.volume_level * 100

    def setMedia(self, mediaStatus: MediaStatus):
        if hasattr(mediaStatus, 'player_state') and mediaStatus.player_state is not None:
            self.__player_state = mediaStatus.player_state

        if hasattr(mediaStatus , 'volume_level'):
            self.__volume_level = round(mediaStatus.volume_level * 100)

        ch = None
        if hasattr(mediaStatus, 'supports_pause'):
            self.__pause = mediaStatus.supports_pause
        else:
            self.__pause = False

        if hasattr(mediaStatus, 'supports_skip_forward'):
            self.__skip_fwd = mediaStatus.supports_skip_forward
        else:
            self.__skip_fwd = False

        if hasattr(mediaStatus, 'supports_skip_backward'):
            self.__skip_bck = mediaStatus.supports_skip_backward
        else:
            self.__skip_bck = False

        if hasattr(mediaStatus, 'supports_stream_volume'):
            self.__volume = mediaStatus.supports_stream_volume
        else:
            self.__volume = False

        if hasattr(mediaStatus, 'title'):
            self.__title = mediaStatus.title

        if hasattr(mediaStatus, 'artist'):
            self.__artist = mediaStatus.artist

        if hasattr(mediaStatus, 'album_name'):
            self.__album = mediaStatus.album_name
