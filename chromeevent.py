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
                self.status = ChromeState(device.device.friendly_name)
                if self.device.cast_type != 'audio':
                        self.status.chromeApp = 'Backdrop'
                
        
        def getChannelList(self):
                if (self.device.cast_type == 'audio'):
                        return self.streams.getChannelList('audio/mp3')
                else:
                        return self.streams.getChannelList('video/mp4')

        def new_cast_status(self, status):
                print("----------- new cast status ---------------")
                print(status)
                appName = status.display_name
                if (appName == "Backdrop"):
                        self.clear()
                if (appName == None):
                        appName = "None"
                        self.clear()
                url = "http://jarvis:8080/json.htm?type=command&param=udevice&idx="+str(self.idx)+"&nvalue=0&svalue="+str(urllib.request.pathname2url(appName))
                try:
                        dom = requests.get(url)
                except:
                        print ("Silently.. domoticz down")
                if self.device.media_controller.status.player_state == "PLAYING": 
                        self.state()
                else:
                        self.status.chromeApp = appName
                self.notifyNodeRed(self.status)

        def new_media_status(self, status):
                print("----------- new media status ---------------")
                print(status)
                if (status.player_state != self.status.player_state) :
                        self.createstate(status)
                        self.notifyNodeRed(self.status)
                if self.status.player_state == 'PLAYING':
                        # Netflix is not reporting nicely on play / pause state changes, so we poll it to get an up to date status
                        if self.status.chromeApp == 'Netflix':
                                time.sleep(1);
                                self.device.media_controller.update_status();

                        # The following is needed to update radio / tv programme displayed on dashboard
                        if self.status.chromeApp == 'Radio' or self.status.chromeApp == 'TV' or self.status.chromeApp == 'DR TV' :
                                time.sleep(20);
                                self.device.media_controller.update_status();

        def notifyNodeRed(self, msg):
                nodeRedURL = 'http://jarvis:1880/node/chromecast'
                req = urllib.request.Request(nodeRedURL)
                req.add_header('Content-Type', 'application/json; charset=utf-8')
                jsondata = json.dumps(msg, default=lambda o: o.__dict__)
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
                print("QUIT!");
                self.device.media_controller.stop()
                self.device.quit_app()
                self.clear()
        
        def clear(self):
                self.status.clear()
        
        def play(self, media = None):
                if media == None:
                        self.device.media_controller.play()
                else:
                        newMedia = self.streams.getChannelData(channelId = media)
                        if (self.device.status.app_id != None):
                                x = self.state()
                                if (x.player_state == "PLAYING"):
                                        if (x.content == newMedia.link):
                                                return
                        self.device.media_controller.play_media(newMedia.link, newMedia.media);
                        self.notifyNodeRed(self.state())

        def createstate(self,s):
                if hasattr(s, 'supports_pause'):
                        self.status.pause = s.supports_pause; 
                else:
                        self.status.pause = False;
                if hasattr(s, 'supports_skip_forward'):
                        self.status.skip_fwd = s.supports_skip_forward
                else:
                        self.status.skip_fwd = False
                if hasattr(s, 'supports_skip_backward'):
                        self.status.skip_bck = s.supports_skip_backward
                else:
                        self.status.skip_bck = False
                if hasattr(s, 'player_state'):
                        if s.player_state != None:
                                self.status.player_state = s.player_state

                ch = self.streams.getChannelData(link=s.content_id)
                if s.media_metadata != None: 
                        if hasattr(s.media_metadata, 'channel'):
                                ch = self.streams.getChannelData(ch=s.media_metadata.channel)                
                if ch.friendly != None:
                # Assume that it is a streaming radio / video channel if we can resolve
                # a friendly name for the s.content_id
                        d = dr(ch.xmlid)
                        self.status.content = s.content_id
                        self.status.title =  ch.friendly + " - " + d.title()
                        self.status.artist = None
                        self.status.album = None
                        self.status.media = ch.media
                        self.status.chromeApp = 'Radio'
                        self.status.id = ch.id
                        # If it's not an audio device, then it must be a video, aka TV channel
                        if self.device.cast_type != 'audio':
                                self.status.chromeApp = 'TV'
                else:
                        self.status.id = None               
                        if self.status.chromeApp == 'Netflix':
                                d = netflix(s.content_id)
                                self.status.title = d.title()
                                
                        if hasattr(s, 'title'):
                                self.status.title = s.title
                        if hasattr(s, 'artist'):
                                self.status.artist = s.artist
                                self.status.album = s.album_name

                url = "http://jarvis:8080/json.htm?type=command&param=udevice&idx=170&nvalue=0&svalue="+str(urllib.request.pathname2url(self.status.player_state))
                try:
                        dom = requests.get(url)
                except:
                        print ("Silently dropped.. domoticz down");
                return self.status 
  
        def state(self):
                if (self.device.status.app_id == None):
                        self.status.clear()
                        return self.status
                if (self.device.status.app_id == 'E8C28D3C'):
                        self.status.clear()
                        return self.status
                s = self.device.media_controller.status
                return self.createstate(s)
                
        def state_json(self):
                return json.dumps(self.state(), default=lambda o: o.__dict__)  



class ChromeState:
        device_name = ""
        title = ""
        player_state = "STOPPED"
        artist = ""
        chromeApp = ""
        content = ""
        album = ""
        media = ""
        id = None
        skip_fwd = False
        skip_bck = False
        pause = False
        
        def __init__(self, device_name):
                self.device_name = device_name

        def clear(self):
                self.title = ""
                self.player_state = "STOPPED"
                self.artist = ""
                self.chromeApp = ""
                self.content = ""
                self.album = ""
                self.media = ""
                self.id = ""
                self.pause = False
                self.skip_fwd = False
                self.skip_bck = False

                