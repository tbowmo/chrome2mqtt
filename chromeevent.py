from urllib import request
import requests
import pychromecast
import json

class ChromeStatusUpdater:
        def __init__(self, device, idx):
                self.idx = idx
                self.device = device
                self.device.register_status_listener(self)
                self.channels = {}
        
        def addChannel(self, link = "", name = "", friendly = "", extra = "", media="audio/mp3"):
                if name == "":
                        name = friendly.replace("_", " ")
                self.channels.update({name:{'link':link, 'name':name,'friendly':friendly,'extra':extra, 'media':media}})
        
        def getChannelList(self):
                return self.channels

        def new_cast_status(self, new_status):
                appName = new_status.display_name
                if (appName == None):
                        appName = "None"
                url = "http://jarvis:8080/json.htm?type=command&param=udevice&idx="+str(self.idx)+"&nvalue=0&svalue="+str(request.pathname2url(appName))
                dom = requests.get(url)

        def new_media_status(self, status):
                pass
        
        def stop(self):
                self.device.media_controller.stop()
        
        def pause(self):
                self.device.media_controller.pause()
        
        def skip(self):
                self.device.media_controller.skip()
                
        def quit(self):
                self.device.quit_app()
        
        def play(self, media = None):
                if media == None:
                        self.device.media_controller.play()
                else:
                        x = self.state()
                        if (x['state'] == "PLAYING"):
                                if (x['content'] == self.channels[media]['link']):
                                        return
                        self.device.media_controller.play_media(self.channels[media]['link'], self.channels[media]['media']);
        
        def state(self):
                s = self.device.media_controller.status
                status = {
                        'state' : s.player_state,
                        'content' : s.content_id,
                        'channel' : self.getChannel(s.content_id),
                        'track'   : 'N/A',
                        'artist'  : 'N/A',
                        'album'   : 'N/A'
                }
                if hasattr(s, 'title'):
                        status['track'] = s.title
                if hasattr(s, 'artist'):
                        if s.artist != None:
                                status['artist'] = s.artist
                                status['channel'] = 'TIDAL'
                        return status 
  
        def state_json(self):
                return json.dumps(self.state())  
        
        def getChannel(self, content):
                for key in self.channels:
                        if content == self.channels[key]['link']:
                                return self.channels[key]['friendly'];
                return "N/A"
        