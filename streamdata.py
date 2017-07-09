import hashlib
from dr import dr

class streamdata:
    def __init__(self):
        self.channels = []
    
    def addChannel(self, channel): #link = "", friendly = "", extra = "", media="audio/mp3", xmlid=""):
#        id = hashlib.md5(friendly.encode('utf-8')).hexdigest()
        self.channels.append(channel) #{'id':id[:8], 'link':link, 'friendly':friendly,'extra':extra, 'media':media, 'xmlid':xmlid, 'tv' : "", 'start':"", 'stop':""})

    def getChannelList(self, media):
        retCh = []
        for channel in self.channels :
            if (channel.media == media):
                if channel.xmlid != "":
                    d = dr(channel.xmlid)
                    channel.tv = d.title()
                    channel.start = d.start()
                    channel.stop = d.stop()
                retCh.append(channel)
        return retCh

    def getChannelData(self, channelId = None, link = None, ch = None):
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
        return stream(friendly = None, media= None)


class stream:
    tv = ""
    start = ""
    stop = ""
    
    def __init__(self, link = "", friendly = "", extra = "", media = "audio/mp3", xmlid = ""):
        if friendly != None: 
            self.id = hashlib.md5(friendly.encode('utf-8')).hexdigest()[:8]
        self.link = link
        self.friendly = friendly
        self.extra = extra
        self.media = media
        self.xmlid = xmlid
