"""
    Handles events from a chromecast device, and reports these to various endpoints
"""

import time
from chromestate import ChromeState
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt_client
import os
import sys
from logger import setup_custom_logger

class ChromeEvent:
    """ Chrome event handling """
    def __init__(self, device, streams):

        self.mqtthost = os.environ['MQTT_HOST']
        self.mqttport = int(os.environ['MQTT_PORT'])
        self.mqttroot = os.environ['MQTT_ROOT']

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
        self.log = setup_custom_logger('ChromeEvent')

    def on_mqtt_message(self, client, userdata, message):
        parameter = message.payload.decode("utf-8")
        cmd = os.path.basename(os.path.normpath(message.topic))
        if cmd == 'play':
            self.play(parameter)
        else:
            if parameter == 'pause':
                self.pause()
            if parameter == 'fwd':
                self.fwd()
            if parameter == 'rev':
                self.rev()
            if parameter == 'quit':
                self.quit()
            if parameter == 'stop':
                self.stop()
            if parameter == 'play':
                self.play()

    def on_mqtt_disconnect(self, client, userdata, rc):
        self.log.info(self.device.cast_type)
        self.log.info(rc)
    

    def getChannelList(self):
        if self.device.cast_type == 'audio':
            return self.streams.get_channel_list('audio/mp3')
        else:
            return self.streams.get_channel_list('video/mp4')

    def new_cast_status(self, status):
        self.log.info("----------- new cast status ---------------")
        self.log.info(status)
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
        publish.single('chromecast/app',  app_name, hostname=self.mqtthost, port=self.mqttport, retain=True)

    def new_media_status(self, status):
        self.log.info("----------- new media status ---------------")
        self.log.info(status)
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
            {'topic': 'chromecast/media', 'payload': msg.json(), 'retain': True },
            {'topic': self.mqttroot + '/state', 'payload': msg.player_state, 'retain': True },            
            {'topic': 'chromecast/state', 'payload': msg.player_state, 'retain': True },            
            ]
        publish.multiple( msg , hostname=self.mqtthost, port=self.mqttport)

    def stop(self):
        """ Stop playing on the chromecast """
        try:
            self.device.media_controller.stop()
            self.status.clear()
        except:
            self.handle_error()

    def pause(self):
        """ Pause playback """
        try:
            self.device.media_controller.pause()
        except:
            self.handle_error()           

    def fwd(self):
        """ Skip to next track """
        try:
            self.device.media_controller.skip()
        except:
            self.handle_error()

    def rev(self):
        """ Rewind to previous track """
        try: 
            self.device.media_controller.rewind()
        except:
            self.handle_error()

    def quit(self):
        """ Quit running application on chromecast """
        try:
            self.device.media_controller.stop()
            self.device.quit_app()
            self.status.clear()
        except:
            self.handle_error()

    def play(self, media=None):
        """ Play a media URL on the chromecast """
        try:
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
        except:
            self.handle_error()

    def handle_error(self):
        sys.exit(1)

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
