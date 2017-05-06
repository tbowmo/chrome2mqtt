import urllib.request 
import requests
import pychromecast
import json
from netflix import netflix
from dr import dr
import time

class ChromeStatusUpdater:
        def __init__(self, device, idx, streams):
                self.streams = streams
                self.idx = idx
                self.type = device.device.cast_type
                self.device = device
                self.device.register_status_listener(self)
                self.device.media_controller.register_status_listener(self)
                self.status = {'device_name':device.device.friendly_name, 'title':None, 'player_state':None, 'artist': None, 'chromeApp':None, 'content':None, 'album':None, 'media':None, 'id': None}
                if self.device.cast_type != 'audio':
                        self.status.update({'chromeApp':'Backdrop'})
                print (device)
                
        
        def getChannelList(self):
                if (self.device.cast_type == 'audio'):
                        return self.streams.getChannelList('audio/mp3')
                else:
                        return self.streams.getChannelList('video/mp4')

        def new_cast_status(self, status):
                appName = status.display_name
                if (appName == "Backdrop"):
                        self.clear()
                if (appName == None):
                        appName = "None"
                        self.clear()
                url = "http://jarvis:8080/json.htm?type=command&param=udevice&idx="+str(self.idx)+"&nvalue=0&svalue="+str(urllib.request.pathname2url(appName))
                dom = requests.get(url)
                self.status.update({'chromeApp':appName})
                self.notifyNodeRed(self.status)

        def new_media_status(self, status):
                if (status.player_state != self.status['player_state']) :
                        self.createstate(status)
                        self.notifyNodeRed(self.status)
                if self.status['player_state'] == 'PLAYING' and self.status['chromeApp'] == 'Netflix':
                        time.sleep(1);
                        self.device.media_controller.update_status();
                if self.status['chromeApp'] == 'Radio' or self.status['chromeApp'] == 'TV' or self.status['chromeApp'] == 'DR TV' :
                        time.sleep(20);
                        self.device.media_controller.update_status();
        
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
                self.clear()
        
        def pause(self):
                self.device.media_controller.pause()
        
        def skip(self):
                self.device.media_controller.skip()
                
        def quit(self):
                self.device.quit_app()
                self.clear()
        
        def clear(self):
                self.status['title'] = ''
                self.status['artist'] = ''
                self.status['album'] = ''
                self.status['content'] = ''
                self.status['player_state'] = 'STOPPED';
        
        def play(self, media = None):
                if media == None:
                        self.device.media_controller.play()
                else:
                        newMedia = self.streams.getChannelData(channelId = media)
                        x = self.state()
                        if (x['player_state'] == "PLAYING"):
                                if (x['content'] == newMedia['link']):
                                        return
                        self.device.media_controller.play_media(newMedia['link'], newMedia['media']);

        def createstate(self,s):
                ch = self.streams.getChannelData(link=s.content_id)
                
                if ch.friendly != None:
                # Assume that it is a streaming radio / video channel if we can resolve
                # a friendly name for the s.content_id
                        d = dr(ch.xmlid)
                        self.status.update({
                                'content' : s.content_id,
                                'title'   : ch.friendly + " - " + d.title(),
                                'artist'  : None,
                                'album'   : None,
                                'media'   : ch.media,
                                'chromeApp' : 'Radio',
                                'id'	  : ch.id
                        })
                        # If it's not an audio device, then it must be a video, aka TV channel
                        if self.device.cast_type != 'audio':
                                self.status.update({'chromeApp': 'TV'})
                else:
                        self.status.update({'id': None})                
                if self.status['chromeApp'] == 'Netflix':
                        d = netflix(s.content_id)
                        self.status.update({'title':d.title()})
                                
                if hasattr(s, 'player_state'):
                        if s.player_state != None:
                                self.status.update({'player_state':s.player_state})
                if hasattr(s, 'title'):
                        if s.title != None:
                                self.status.update({'title': s.title})
                if hasattr(s, 'artist'):
                        if s.artist != None:
                                self.status.update({'artist' : s.artist, 'album':s.album_name});

                print (self.status)
                url = "http://jarvis:8080/json.htm?type=command&param=udevice&idx=170&nvalue=0&svalue="+str(urllib.request.pathname2url(self.status['player_state']))
                dom = requests.get(url)
                return self.status 
  
        def state(self):
                s = self.device.media_controller.status
                return self.createstate(s)
                
        def state_json(self):
                return json.dumps(self.state())  
