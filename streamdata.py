class streamdata:
  def __init__(self):
    self.channels = []
  
  def addChannel(self, link = "", name = "", friendly = "", extra = "", media="audio/mp3"):
    if name == "":
      name = friendly.replace(" ", "_")
    self.channels.append({'link':link, 'name':name,'friendly':friendly,'extra':extra, 'media':media})

  def getChannelList(self, media):
    retCh = []
    for channel in self.channels :
      if (channel['media'] == media):
        retCh.append(channel)
    return retCh

  def getChannelData(self, channelName = None, link = None):
    for channel in self.channels :
      if channelName != None: 
        if channel['name'] == channelName:
          return channel
      if link != None:
        if channel['link'] == link:
          return channel
    return None
    