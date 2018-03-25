"""
    holds current state of the chromedevice
"""
import json
from dr import Dr
from netflix import Netflix

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
            "player_state": self.player_state
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

    def update(self, player, streams):
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
        try:
            if player.media_metadata is not None:
                if hasattr(player.media_metadata, 'channel'):
                    ch = streams.get_channel_data(ch=player.media_metadata.channel)
            if ch is None:
                ch = streams.get_channel_data(link=player.content_id)
        except:
            print('"silently" thrown error away')

        if ch is not None and ch.friendly is not None:
        # Assume that it is a streaming radio / video channel if we can resolve
        # a friendly name for the s.content_id
            d = Dr(ch.xmlid)
            self.content = player.content_id
            self.title = ch.friendly + " - " + d.title()
            self.artist = None
            self.album = None
            self.media = ch.media
            self.id = ch.id
        else:
            self.id = None
            if self.__chrome_app == 'Netflix':
                d = Netflix(player.content_id)
                self.title = d.title()

            if hasattr(player, 'title'):
                self.title = player.title

            if hasattr(player, 'artist'):
                self.artist = player.artist

            if hasattr(player, 'album_name'):
                self.album = player.album_name
