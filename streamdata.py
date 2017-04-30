import hashlib
from dr import dr

class streamdata:
  def __init__(self):
    self.channels = []
  
  def addChannel(self, link = "", friendly = "", extra = "", media="audio/mp3", xmlid=""):
    id = hashlib.md5(friendly.encode('utf-8')).hexdigest()
    self.channels.append({'id':id[:8], 'link':link, 'friendly':friendly,'extra':extra, 'media':media, 'xmlid':xmlid, 'tv' : "", 'start':"", 'stop':""})

  def getChannelList(self, media):
    retCh = []
    for channel in self.channels :
      if (channel['media'] == media):
        if channel['xmlid'] != "":
          d = dr(channel['xmlid'])
          channel.update({'tv': d.title(), 'start':d.start(),'stop':d.stop()})
        retCh.append(channel)
    return retCh

  def getChannelData(self, channelId = None, link = None):
    for channel in self.channels :
      if channelId != None: 
        if channel['id'] == channelId:
          return channel
      if link != None:
        if channel['link'] in link:
          return channel
    return {'friendly':None, 'media':None}

