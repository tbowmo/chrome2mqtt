from time import sleep
from chrome2mqtt.chromestate import ChromeState
from os import path
import logging
from chrome2mqtt.mqtt import MQTT
from pychromecast import Chromecast
from chrome2mqtt.command import Command, CommandResult

class ChromeEvent:
    """ 
        Handles events from a chromecast device, and reports these to various endpoints
    """
    device: Chromecast = None
    last_media = None
    last_state = None
    def __init__(self, device: Chromecast,  mqtt: MQTT):
        self.device = device
        self.mqtt = mqtt
        self.name = self.device.device.friendly_name.lower().replace(' ', '_')
        self.mqttpath = self.name
        self.log = logging.getLogger('ChromeEvent_' + self.device.cast_type)

        self.device.register_status_listener(self)
        self.device.media_controller.register_status_listener(self)

        self.status = ChromeState(device.device)
        
        controlPath = self.name + '/control/#'
        self.mqtt.subscribe(controlPath)
        self.mqtt.message_callback_add(controlPath, self.__mqtt_action)
        self.device.wait()
        self.__command = Command(self.device, self.status)

    def __mqtt_action(self, client, userdata, message):
        parameter = message.payload.decode("utf-8")
        command = path.basename(path.normpath(message.topic))
        self.action(command, parameter)
        
    def action(self, command, parameter):
        if self.__command.execute(command, parameter) == CommandResult.NoCommand:
            self.log.warn('Fallback to command via payload, or command "{0}'.format(command))
            if self.__command.execute(parameter, None) == CommandResult.NoCommand:
                self.log.error('Control command not supported "{0}" with parameter "{1}"'.format(command, parameter))

    def new_cast_status(self, status):
        self.log.info("----------- new cast status ---------------")
        self.log.info(status)
        self.status.setState(status)
        self.__mqtt_publish(self.state())

    def new_media_status(self, status):
        self.log.info("----------- new media status ---------------")
        self.log.info(status)
        self.__createstate(status)
        self.__mqtt_publish(self.status)
        if self.status.player_state == 'PLAYING':
            # Netflix is not reporting nicely on play / pause state changes, so we poll it to get an up to date status
            if self.status.app == 'Netflix':
                sleep(1)
                self.device.media_controller.update_status()

    def __mqtt_publish(self, msg: ChromeState):
        media = msg.media
        state = msg.state
        if (self.last_media != media):            
            # Only send new update, if title or player_state has changed.
            self.mqtt.publish(self.mqttpath + '/media', media, retain = True )
            self.last_media = media
        if (self.last_state != state):
            self.mqtt.publish(self.mqttpath + '/capabilities', state, retain = True )
            self.mqtt.publish(self.mqttpath + '/state', msg.player_state, retain = True )
            self.mqtt.publish(self.mqttpath + '/volume', msg.volume_level, retain = True )
            self.mqtt.publish(self.mqttpath + '/app', msg.app, retain=True)

            self.last_state = state

    def __createstate(self, state):
        self.status.setMedia(state)
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

