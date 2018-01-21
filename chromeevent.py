""" 
    Handles events from a chromecast device, and reports these to various endpoints
"""

import json
import urllib.request
import time
import requests
from netflix import Netflix
from dr import Dr

class ChromeEvent:
    """ Chrome event handling """
    def __init__(self, device, idx, streams):
        self.streams = streams
        self.idx = idx
        self.type = device.device.cast_type
        self.device = device
        self.device.register_status_listener(self)
        self.device.media_controller.register_status_listener(self)
        self.status = ChromeState(device.device)
        if self.device.cast_type != 'audio':
            self.status.chrome_app = 'Backdrop'

    def getChannelList(self):
        if self.device.cast_type == 'audio':
            return self.streams.getChannelList('audio/mp3')
        else:
            return self.streams.getChannelList('video/mp4')

    def __new_cast_status(self, status):
        print("----------- new cast status ---------------")
        print(status)
        app_name = status.display_name
        if app_name == "Backdrop":
            self.status.clear()
        if app_name is None:
            app_name = "None"
            self.status.clear()
        self.__notify_domoticz(app_name, self.idx)
        if self.device.media_controller.status.player_state == "PLAYING":
            self.state()
        else:
            self.status.chrome_app = app_name
        self.__notify_node_red(self.status)

    def __new_media_status(self, status):
        print("----------- new media status ---------------")
        print(status)
        if status.player_state != self.status.player_state:
            self.__createstate(status)
            self.__notify_node_red(self.status)
        if self.status.player_state == 'PLAYING':
            # Netflix is not reporting nicely on play / pause state changes, so we poll it to get an up to date status
            if self.status.chrome_app == 'Netflix':
                time.sleep(1)
                self.device.media_controller.update_status()

            # The following is needed to update radio / tv programme displayed on dashboard
            if self.status.chrome_app == 'Radio' or self.status.chrome_app == 'TV' or self.status.chrome_app == 'DR TV' :
                time.sleep(20)
                self.device.media_controller.update_status()

    def __notify_node_red(self, msg):
        node_red_url = 'http://localhost:1880/node/chromecast'
        req = urllib.request.Request(node_red_url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(msg, default=lambda o: o.__dict__)
        jsondataasbytes = jsondata.encode('utf-8')
        req.add_header('Content-Length', len(jsondataasbytes))
        urllib.request.urlopen(req, jsondataasbytes)

    def __notify_domoticz(self, msg, device):
        url = "http://localhost:8080/json.htm?type=command&param=udevice&idx="+str(device)+"&nvalue=0&svalue="+str(urllib.request.pathname2url(msg))
        print("------ Domoticz ------")
        print(url)
        try:
            requests.get(url)
        except requests.exceptions.RequestException:
            print("Silently.. domoticz down")

    def stop(self):
        """ Stop playing on the chromecast """
        self.device.media_controller.stop()
        self.status.clear()

    def pause(self):
        """ Pause playback """
        self.device.media_controller.pause()

    def skip(self):
        """ Skip to next track """
        self.device.media_controller.skip()

    def quit(self):
        """ Quit running application on chromecast """
        self.device.media_controller.stop()
        self.device.quit_app()
        self.status.clear()

    def play(self, media=None):
        """ Play a media URL on the chromecast """
        if media is None:
            self.device.media_controller.play()
        else:
            new_media = self.streams.getChannelData(channelId=media)
            if self.device.status.app_id != None:
                x = self.state()
                if x.player_state == "PLAYING":
                    if x.content == new_media.link:
                        return
            self.device.media_controller.play_media(new_media.link, new_media.media)
            self.__notify_node_red(self.state())

    def __createstate(self,s):
        if hasattr(s, 'supports_pause'):
            self.status.pause = s.supports_pause
        else:
            self.status.pause = False
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
            d = Dr(ch.xmlid)
            self.status.content = s.content_id
            self.status.title = ch.friendly + " - " + d.title()
            self.status.artist = None
            self.status.album = None
            self.status.media = ch.media
            self.status.chrome_app = 'Radio'
            self.status.id = ch.id
            # If it's not an audio device, then it must be a video, aka TV channel
            if self.device.cast_type != 'audio':
                self.status.chrome_app = 'TV'
        else:
            self.status.id = None
            if self.status.chrome_app == 'Netflix':
                d = Netflix(s.content_id)
                self.status.title = d.title()
            if hasattr(s, 'title'):
                self.status.title = s.title
            if hasattr(s, 'artist'):
                self.status.artist = s.artist
                self.status.album = s.album_name
        self.__notify_domoticz(self.status.player_state, 170)
        return self.status

    def state(self):
        """ Return state of the player """
        if self.device.status.app_id is None:
            self.status.clear()
            return self.status
        if self.device.status.app_id == 'E8C28D3C':
            self.status.clear()
            return self.status
        s = self.device.media_controller.status
        return self.__createstate(s)


class ChromeState:
    """ Holds state of the chromecast player """
    device_name = ""
    device_type = ""
    title = ""
    player_state = "STOPPED"
    artist = ""
    chrome_app = ""
    content = ""
    album = ""
    media = ""
    id = None
    skip_fwd = False
    skip_bck = False
    pause = False

    def __init__(self, device):
        self.device_name = device.friendly_name
        if device.cast_type == 'cast':
            self.device_type = 'video'
        else:
            self.device_type = device.cast_type

    def clear(self):
        """ Clear all fields """
        self.title = ""
        self.player_state = "STOPPED"
        self.artist = ""
        self.chrome_app = ""
        self.content = ""
        self.album = ""
        self.media = ""
        self.id = ""
        self.pause = False
        self.skip_fwd = False
        self.skip_bck = False
