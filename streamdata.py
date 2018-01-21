"""
 Handles stream descriptors
"""
import hashlib
from dr import Dr

class StreamData:
    """ Handles stream descriptors, searching and listing all channels """
    def __init__(self):
        self.channels = []

    def addChannel(self, channel):
        """ Add channel to repository """
        self.channels.append(channel)

    def getChannelList(self, media = "Audio/mp3"):
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

    def getChannelData(self, channelId = None, link = None, ch = None):
        """ Get data for a single channel """
        for channel in self.channels :
            if channelId != None: 
                if channel.id == channelId:
                    return channel
            if link != None:
                if channel.link in link:
                    return channel
            if ch != None:
                if channel.friendly == ch:
                    return channel
        return Stream(friendly = None, media= None)


class Stream:
    """ Single streaming channel data """
    tv = ""
    start = ""
    stop = ""
    id = ""
    def __init__(self, link = "", friendly = "", extra = "", media = "audio/mp3", xmlid = ""):
        if friendly != "" and friendly is not None: 
            self.id = hashlib.md5(friendly.encode('utf-8')).hexdigest()[:8]
        self.link = link
        self.friendly = friendly
        self.extra = extra
        self.media = media
        self.xmlid = xmlid
