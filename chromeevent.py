"""
    Handles events from a chromecast device, and reports these to various endpoints
"""

from time import sleep
from chromestate import ChromeState
from os import path
from sys import exit
from logger import setup_custom_logger

class ChromeEvent:
    """ Chrome event handling """
    def __init__(self, device, streams,  mqtt, mqttroot):

        self.device = device
        self.device.register_status_listener(self)
        self.device.media_controller.register_status_listener(self)

        self.mqtt = mqtt

        self.mqttroot = mqttroot
        self.status = ChromeState(device.device)
        if self.device.cast_type != 'audio':
            self.status.setApp('Netflix')
        self.mqttpath = self.mqttroot + '/' + self.device.cast_type

        self.mediax = ''
        self.statex = ''
        self.streams = streams
        controlPath = self.mqttpath + '/control/#'
        self.mqtt.subscribe(controlPath)
        self.mqtt.message_callback_add(controlPath, self.mqtt_action)
        self.log = setup_custom_logger('ChromeEvent_' + self.device.cast_type)

    def mqtt_action(self, client, userdata, message):
        parameter = message.payload.decode("utf-8")
        cmd = path.basename(path.normpath(message.topic))
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
        self.mqtt.publish(self.mqttpath+'/app', app_name, retain=True)
        self.mqtt.publish(self.mqttroot+'/app',  app_name, retain=True)

    def new_media_status(self, status):
        self.log.info("----------- new media status ---------------")
        self.log.info(status)
        self.__createstate(status)
        self.__mqtt_publish(self.status)
        if self.status.player_state == 'PLAYING':
            # Netflix is not reporting nicely on play / pause state changes, so we poll it to get an up to date status
            if self.status.app() == 'Netflix':
                self.log.info("Reloading netflix status")
                sleep(1)
                self.device.media_controller.update_status()

            # The following is needed to update radio / tv programme displayed on dashboard
            if self.status.app() == 'Radio' or self.status.app() == 'TV' or self.status.app() == 'DR TV' :
                self.log.info("Reloading DR status")
                sleep(20)
                self.device.media_controller.update_status()

    def __mqtt_publish(self, msg):
        mqtt_msg = []
        if (self.statex != msg.player_state):
            self.mqtt.publish(self.mqttpath + '/state', msg.player_state, retain = True )
            self.mqtt.publish(self.mqttroot + '/state', msg.player_state, retain = True )
            self.statex = msg.player_state
        if (self.mediax != msg.json()):            
            self.mqtt.publish(self.mqttpath + '/media', msg.json(), retain = True )
            self.mqtt.publish(self.mqttroot + '/media', msg.json(), retain = True )
            self.mediax = msg.json()

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
        exit(1)

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
