"""
    Handles events from a chromecast device, and reports these to various endpoints
"""

import configparser
import time
from chromestate import ChromeState
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt_client
import os

class ChromeEvent:
    """ Chrome event handling """
    def __init__(self, device, streams):
        config = configparser.ConfigParser()
        config.read('/config/config.ini')
        self.mqtthost = "jarvis"
        self.mqttport = 1883
        self.mqttroot = 'chromecast'
        if "default" in config:
            default = config['default']
            if 'mqtthost' in default:
                self.mqtthost = default['mqtthost']
            if 'mqttport' in default:
                self.mqttport = int(default['mqttport'])
            if 'mqttroot' in default:
                self.mqttroot = default['mqttroot']
        self.streams = streams
        self.device = device
        self.device.register_status_listener(self)
        self.device.media_controller.register_status_listener(self)
        self.status = ChromeState(device.device)
        if self.device.cast_type != 'audio':
            self.status.setApp('Backdrop')
        self.mqttroot = self.mqttroot + '/' + self.device.cast_type
        client = mqtt_client.Client(self.device.cast_type + '_client')
        client.on_message = self.on_mqtt_message
        client.connect(self.mqtthost)
        client.loop_start()
        client.subscribe(self.mqttroot + '/control/#')
        client.on_disconnect = self.on_mqtt_disconnect

    def on_mqtt_message(self, client, userdata, message):
        parameter = message.payload.decode("utf-8")
        cmd = os.path.basename(os.path.normpath(message.topic))
        if cmd == 'stop':
            self.stop()
        if cmd == 'play':
            if parameter == '':
                self.play()
            else: 
                self.play(parameter)
        if cmd == 'pause':
            self.pause()
        if cmd == 'skip':
            self.skip()
        if cmd == 'quit':
            self.quit()

    def on_mqtt_disconnect(self, client, userdata, rc):
        print(self.device.cast_type)
        print(rc)
    

    def getChannelList(self):
        if self.device.cast_type == 'audio':
            return self.streams.get_channel_list('audio/mp3')
        else:
            return self.streams.get_channel_list('video/mp4')

    def new_cast_status(self, status):
        print("----------- new cast status ---------------")
        print(status)
        app_name = status.display_name
        if app_name == "Backdrop":
            self.status.clear()
        if (app_name is None) or (app_name == ""):
            app_name = "None"
            self.status.clear()

        self.status.setApp(app_name)

        if self.device.media_controller.status.player_state == "PLAYING":
            self.state()
        publish.single(self.mqttroot+'/app', app_name, hostname=self.mqtthost, port=self.mqttport, retain=True)

    def new_media_status(self, status):
        print("----------- new media status ---------------")
        print(status)
        self.__createstate(status)
        self.__mqtt_publish(self.status)
        if self.status.player_state == 'PLAYING':
            # Netflix is not reporting nicely on play / pause state changes, so we poll it to get an up to date status
            if self.status.app() == 'Netflix':
                time.sleep(1)
                self.device.media_controller.update_status()

            # The following is needed to update radio / tv programme displayed on dashboard
            if self.status.app() == 'Radio' or self.status.app() == 'TV' or self.status.app() == 'DR TV' :
                time.sleep(20)
                self.device.media_controller.update_status()

    def __mqtt_publish(self, msg):
        msg = [
            {'topic': self.mqttroot + '/media', 'payload': msg.json(), 'retain': True },
            {'topic': self.mqttroot + '/state', 'payload': msg.player_state, 'retain': True },            
            ]
        publish.multiple( msg , hostname=self.mqtthost, port=self.mqttport)

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
            new_media = self.streams.get_channel_data(channelId=media)
            if self.device.status.app_id is not None:
                x = self.state()
                if x.player_state == "PLAYING":
                    if x.content == new_media.link:
                        return
            self.device.media_controller.play_media(new_media.link, new_media.media)
            self.__mqtt_publish(self.state())

    def __createstate(self, state):
        self.status.update(state, self.streams)
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

    def state_json(self):
        """ Returns status as json encoded string """
        return self.status.json()
