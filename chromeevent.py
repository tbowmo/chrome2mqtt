"""
    Handles events from a chromecast device, and reports these to various endpoints
"""

from time import sleep
from chromestate import ChromeState
from os import path
from sys import exit
import logging
from mqtt import MQTT

class ChromeEvent:
    """ Chrome event handling """
    device = None
    last_media = None
    last_state = None
    def __init__(self, device,  mqtt: MQTT):
        self.device = device
        self.mqtt = mqtt
        self.name = self.device.device.friendly_name.lower().replace(' ', '_')
        self.mqttpath = self.name
        self.log = logging.getLogger('ChromeEvent_' + self.device.cast_type)

        self.device.register_status_listener(self)
        self.device.media_controller.register_status_listener(self)

        self.status = ChromeState(device.device)
        if self.device.cast_type != 'audio':
            self.status.setApp('Backdrop')

        controlPath = self.name + '/control/#'
        self.mqtt.subscribe(controlPath)
        self.mqtt.message_callback_add(controlPath, self.mqtt_action)
        self.device.wait()

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
            if parameter == 'status':
                self.device.media_controller.update_status()

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
            self.log.warn('!!!!!THIS SHOULD NOT BE CALLED!!!!!')
            self.state()
        self.mqtt.publish(self.mqttpath+'/app', app_name, retain=True)

    def new_media_status(self, status):
        self.log.info("----------- new media status ---------------")
        self.log.info(status)
        self.__createstate(status)
        self.__mqtt_publish(self.status)
        if self.status.player_state == 'PLAYING':
            # Netflix is not reporting nicely on play / pause state changes, so we poll it to get an up to date status
            if self.status.app() == 'Netflix':
                sleep(1)
                self.device.media_controller.update_status()

    def __mqtt_publish(self, msg: ChromeState):
        media = msg.json_media()
        state = msg.json_state()
        if (self.last_media != media):            
            # Only send new update, if title or player_state has changed.
            self.mqtt.publish(self.mqttpath + '/media', media, retain = True )
            self.last_media = media
        if (self.last_state != state):
            self.mqtt.publish(self.mqttpath + '/capabilities', state, retain = True )
            self.mqtt.publish(self.mqttpath + '/state', msg.player_state, retain = True )
            self.last_state = state

    def stop(self):
        """ Stop playing on the chromecast """
        try:
            self.device.media_controller.stop()
            self.status.clear()
        except:
            self.__handle_error()

    def pause(self):
        """ Pause playback """
        try:
            self.device.media_controller.pause()
        except:
            self.__handle_error()           

    def fwd(self):
        """ Skip to next track """
        try:
            self.device.media_controller.skip()
        except:
            self.__handle_error()

    def rev(self):
        """ Rewind to previous track """
        try: 
            self.device.media_controller.rewind()
        except:
            self.__handle_error()

    def quit(self):
        """ Quit running application on chromecast """
        try:
            self.device.media_controller.stop()
            self.device.quit_app()
            self.status.clear()
        except:
            self.__handle_error()

    def play(self, media=None):
        """ Play a media URL on the chromecast """
        try:
            if media is None:
                self.device.media_controller.play()
            else:
                self.device.media_controller.play_media(media.link, media.media)
                self.__mqtt_publish(self.state())
        except:
            self.__handle_error()

    def __handle_error(self):
        exit(1)

    def __createstate(self, state):
        self.status.update(state)
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
