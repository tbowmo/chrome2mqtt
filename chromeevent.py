import urllib.request 
import requests
import pychromecast
import json

class ChromeStatusUpdater:
        def __init__(self, device, idx):
                self.idx = idx
                self.device = device
                self.device.register_status_listener(self)
                self.device.media_controller.register_status_listener(self)
                self.channels = {}
                self.status = {'device_name':device.device.friendly_name, 'title':None, 'player_state':None, 'artist': None, 'chromeApp':None}
                print (device)
                
        
        def addChannel(self, link = "", name = "", friendly = "", extra = "", media="audio/mp3"):
                if name == "":
                        name = friendly.replace(" ", "_")
                self.channels.update({name:{'link':link, 'name':name,'friendly':friendly,'extra':extra, 'media':media}})
        
        def getChannelList(self):
                return self.channels

        def new_cast_status(self, status):
                appName = status.display_name
                if (appName == None):
                        appName = "None"
                url = "http://jarvis:8080/json.htm?type=command&param=udevice&idx="+str(self.idx)+"&nvalue=0&svalue="+str(urllib.request.pathname2url(appName))
                dom = requests.get(url)
                self.status.update({'chromeApp':appName})
                self.notifyNodeRed(self.status)

        def new_media_status(self, status):
                self.status.update({'title':status.title, 'player_state' : status.player_state, 'artist': status.artist})
                print (status)
                ch = self.getChannel(status.content_id)
                if ch['friendly'] != "N/A" :
                        self.status.update({'title' : ch['friendly']})                
                self.notifyNodeRed(self.status)
        
        def notifyNodeRed(self, msg):
                nodeRedURL = 'http://jarvis:1880/node/chromecast'
                req = urllib.request.Request(nodeRedURL)
                req.add_header('Content-Type', 'application/json; charset=utf-8')
                print (msg)
                jsondata = json.dumps(msg)
                jsondataasbytes = jsondata.encode('utf-8')
                req.add_header('Content-Length', len(jsondataasbytes))
                print (jsondataasbytes)
                response = urllib.request.urlopen(req, jsondataasbytes)
                
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
                ch = self.getChannel(s.content_id)
                status = {
                        'state' : s.player_state,
                        'content' : s.content_id,
                        'channel' : ch['friendly'],
                        'track'   : 'N/A',
                        'artist'  : 'N/A',
                        'album'   : 'N/A',
                        'media'   : ch['media']
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
                ch = {'friendly':"N/A", 'media':"N/A"}
                if content != None:
                        for key in self.channels:
                                if self.channels[key]['link'] in content:
                                        ch.update(self.channels[key])
                return ch
        
