import urllib.request 
import requests
import pychromecast
import json
from netflix import netflix

class ChromeStatusUpdater:
        def __init__(self, device, idx, streams):
                self.streams = streams
                self.idx = idx
                self.type = device.device.cast_type
                self.device = device
                self.device.register_status_listener(self)
                self.device.media_controller.register_status_listener(self)
                self.status = {'device_name':device.device.friendly_name, 'title':None, 'player_state':None, 'artist': None, 'chromeApp':None, 'content':None, 'album':None, 'media':None}
                print (device)
                
        
        def getChannelList(self):
                if (self.device.cast_type == 'audio'):
                        return self.streams.getChannelList('audio/mp3')
                else:
                        return self.streams.getChannelList('video/mp4')

        def new_cast_status(self, status):
                appName = status.display_name
                if (appName == None):
                        appName = "None"
                url = "http://jarvis:8080/json.htm?type=command&param=udevice&idx="+str(self.idx)+"&nvalue=0&svalue="+str(urllib.request.pathname2url(appName))
                dom = requests.get(url)
                self.status.update({'chromeApp':appName})
                self.notifyNodeRed(self.status)

        def new_media_status(self, status):
                self.status.update({'title':status.title, 'player_state' : status.player_state, 'artist': status.artist, 'album':status.album_name})
                if hasattr(status, 'content_id'):
                        if (self.status['chromeApp'] == 'Netflix'):
                                n = netflix(status.content_id)
                        self.status.update({'title':n.title(), 'content':status.content_id})
                ch = self.getChannel(status.content_id)
                if ch['friendly'] != "N/A" :
                        self.status.update({'title' : ch['friendly'], 'chromeApp':'radio'})                
                self.notifyNodeRed(self.status)
        
        def notifyNodeRed(self, msg):
                nodeRedURL = 'http://jarvis:1880/node/chromecast'
                req = urllib.request.Request(nodeRedURL)
                req.add_header('Content-Type', 'application/json; charset=utf-8')
                print ("--- notifying node-red ---")
                print (msg)
                jsondata = json.dumps(msg)
                print ("--- json data ----")
                print (jsondata)
                jsondataasbytes = jsondata.encode('utf-8')
                req.add_header('Content-Length', len(jsondataasbytes))
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
                        newMedia = self.streams.getChannelData(channelName = media)
                        x = self.state()
                        if (x['player_state'] == "PLAYING"):
                                if (x['content'] == newMedia['link']):
                                        return
                        self.device.media_controller.play_media(newMedia['link'], newMedia['media']);
        
        def state(self):
                s = self.device.media_controller.status
                ch = self.getChannel(s.content_id)
                if ch != None:
                        self.status.update({
                                'content' : s.content_id,
                                'title'   : ch['friendly'],
                                'artist'  : None,
                                'album'   : None,
                                'media'   : ch['media'],
                                'chromeApp' : 'radio'
                        })
                if hasattr(s, 'player_state'):
                        if s.player_state != None:
                                self.status.update({'player_state':s.player_state})
                if hasattr(s, 'title'):
                        if s.title != None:
                                self.status.update({'title': s.title})
                if hasattr(s, 'artist'):
                        if s.artist != None:
                                self.status.update({'artist' : s.artist, 'album':s.album_name});
                return self.status 
  
        def state_json(self):
                self.state()
                return json.dumps(self.status)  
        
        def getChannel(self, content):
                ch = {'friendly':None, 'media':None}
                if content != None:
                        stream = self.streams.getChannelData(link=content)
                        if stream != None:
                                ch.update(stream)
                return ch
        
