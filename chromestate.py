"""
    holds current state of the chromedevice
"""
import json
from logger import setup_custom_logger
class ChromeState:
    """ Holds state of the chromecast player """
    __device_type = ""
    __chrome_app = ""
    title = ""
    artist = ""
    album = ""
    content = ""
    id = ""    
    skip_fwd = False
    skip_bck = False
    pause = False
    player_state = ""

    def __init__(self, device):
        if device.cast_type == 'cast':
            self.__device_type = 'video'
        else:
            self.__device_type = device.cast_type
        self.log = setup_custom_logger('chromestate')

    def __repr__(self):
        return json.dumps(self.dtodict())

    def json(self):
        return json.dumps(self.dtodict()).encode('utf-8')

    def dtodict(self):
        """ Returns a json interpretation of the object """
        return {
            "title": self.title,
            "artist":self.artist,
            "album":self.album,
            "content": self.content,
            "skip_fwd": self.skip_fwd,
            "skip_bck": self.skip_bck,
            "pause": self.pause,
            "id": self.id,
            "player_state": self.player_state,
            "chrome_app": self.__chrome_app
        }

    def clear(self):
        """ Clear all fields """
        self.player_state = "STOPPED"
        self.__chrome_app = ""
        self.id = ""
        self.title = ""
        self.artist = ""
        self.content = ""
        self.album = ""
        self.media = ""
        self.pause = False
        self.skip_fwd = False
        self.skip_bck = False
    
    def setApp(self, appName):
        self.__chrome_app = appName

    def app(self):
        return self.__chrome_app

    def update(self, player):
        if hasattr(player, 'player_state') and player.player_state is not None:
            self.player_state = player.player_state

        ch = None
        if hasattr(player, 'supports_pause'):
            self.pause = player.supports_pause
        else:
            self.pause = False

        if hasattr(player, 'supports_skip_forward'):
            self.skip_fwd = player.supports_skip_forward
        else:
            self.skip_fwd = False

        if hasattr(player, 'supports_skip_backward'):
            self.skip_bck = player.supports_skip_backward
        else:
            self.skip_bck = False

        self.id = None

        if hasattr(player, 'title'):
            self.title = player.title

        if hasattr(player, 'artist'):
            self.artist = player.artist

        if hasattr(player, 'album_name'):
            self.album = player.album_name
