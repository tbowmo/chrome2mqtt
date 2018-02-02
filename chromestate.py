"""
    holds current state of the chromedevice
"""
import json
from dr import Dr
from netflix import Netflix

class ChromeState:
    """ Holds state of the chromecast player """
    device_name = ""
    device_type = ""
    title = ""
    player_state = "STOPPED"
    artist = ""
    chrome_app = ""
    content = ""
    album = ""
    media = ""
    id = None
    skip_fwd = False
    skip_bck = False
    pause = False

    def __init__(self, device):
        self.device_name = device.friendly_name
        if device.cast_type == 'cast':
            self.device_type = 'video'
        else:
            self.device_type = device.cast_type

    def __repr__(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def json(self):
        """ Returns a json interpretation of the object """
        return json.dumps(self, default=lambda o: o.__dict__)

    def clear(self):
        """ Clear all fields """
        self.title = ""
        self.player_state = "STOPPED"
        self.artist = ""
        self.chrome_app = ""
        self.content = ""
        self.album = ""
        self.media = ""
        self.id = ""
        self.pause = False
        self.skip_fwd = False
        self.skip_bck = False

    def update(self, player, streams):

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

        if hasattr(player, 'player_state') and player.player_state is not None:
            self.player_state = player.player_state
        ch = None
        try:
            if player.media_metadata is not None:
                if hasattr(player.media_metadata, 'channel'):
                    ch = streams.get_channel_data(ch=player.media_metadata.channel)
            else:
                ch = streams.get_channel_data(link=player.content_id)
        except:


        if ch is not None and ch.friendly is not None:
        # Assume that it is a streaming radio / video channel if we can resolve
        # a friendly name for the s.content_id
            d = Dr(ch.xmlid)
            self.content = player.content_id
            self.title = ch.friendly + " - " + d.title()
            self.artist = None
            self.album = None
            self.media = ch.media
            self.chrome_app = 'Radio'
            self.id = ch.id
            # If it's not an audio device, then it must be a video, aka TV channel
            if self.device_type != 'audio':
                self.chrome_app = 'TV'
        else:
            self.id = None
            if self.chrome_app == 'Netflix':
                d = Netflix(player.content_id)
                self.title = d.title()

            if hasattr(player, 'title'):
                self.title = player.title

            if hasattr(player, 'artist'):
                self.artist = player.artist

            if hasattr(player, 'album_name'):
                self.album = player.album_name
