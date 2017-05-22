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
                dom = requests.get(url)
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
                self.device.quit_app()
                self.clear()
        
        def clear(self):
                self.status.clear()
        
        def play(self, media = None):
                if media == None:
                        self.device.media_controller.play()
                else:
                        newMedia = self.streams.getChannelData(channelId = media)
                        x = self.state()
                        if (x.player_state == "PLAYING"):
                                if (x.content == newMedia.link):
                                        return
                        self.device.media_controller.play_media(newMedia.link, newMedia.media);

        def createstate(self,s):
                if hasattr(s, 'player_state'):
                        if s.player_state != None:
                                self.status.player_state = s.player_state

                ch = self.streams.getChannelData(link=s.content_id)
                print ("--create state--")
                if s.media_metadata != None: 
                        if 'channel' in s.media_metadata:
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
                dom = requests.get(url)
                return self.status 
  
        def state(self):
                s = self.device.media_controller.status
                print(s);
                return self.createstate(s)
                
        def state_json(self):
                return json.dumps(self.state(), default=lambda o: o.__dict__)  



class ChromeState:
        device_name = None
        title = None
        player_state = "STOPPED"
        artist = None
        chromeApp = None
        content = None
        album = None
        media = None
        id = None
        
        def __init__(self, device_name):
                self.device_name = device_name

        def clear(self):
                title = None
                player_state = "STOPPED"
                artist = None
                chromeApp = None
                content = None
                album = None
                media = None
                id = None
                