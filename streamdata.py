"""
 Handles stream descriptors
"""
import hashlib
import json
from dr import Dr

class StreamData:
    """ Handles stream descriptors, searching and listing all channels """
    def __init__(self):
        self.channels = []

    def add_channel(self, channel):
        """ Add channel to repository """
        self.channels.append(channel)

    def get_channel_list(self, media = "Audio/mp3"):
        """ List all channels for given media, defaults to audio/mp3 """
        ret_ch = []
        for channel in self.channels :
            if channel.media == media:
                if channel.xmlid != "":
                    d = Dr(channel.xmlid)
                    channel.tv = d.title()
                    channel.start = d.start()
                    channel.stop = d.stop()
                ret_ch.append(channel)
        return ret_ch

    def get_channel_data(self, channelId=None, link=None, ch=None):
        """ Get data for a single channel """
        try:
            for channel in self.channels:
                if channelId is not None:
                    if channel.id == channelId:
                        return channel
                if link is not None:
                    if channel.link in link:
                        return channel
                if ch is not None:
                    if channel.friendly == ch:
                        return channel
        except Exception:
            pass
        print('xxx')
        dummy = {'friendly':None, 'media':None}
        return Stream(**dummy)


class Stream:
    """ Single streaming channel data """
    tv = ""
    start = ""
    stop = ""
    id = ""
    friendly = ""
    extra = ""
    xmlid = ""
    link = ""
    friendly = ""
    media = ""
    def __init__(self, **data):
        self.__dict__.update(data)
        if self.friendly != "":
            self.id = hashlib.md5(self.friendly.encode('utf-8')).hexdigest()[:8]

    def __repr__(self):
        return json.dumps(self, default=lambda o: o.__dict__)
