from time import sleep
from chrome2mqtt.chromestate import ChromeState
from os import path
import logging
from chrome2mqtt.mqtt import MQTT
from pychromecast import Chromecast
from chrome2mqtt.command import Command, CommandException

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
        self.log = logging.getLogger('chromevent_{0}'.format(self.device.cast_type))

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
        try:
            result = self.__command.execute(command, parameter)
            if result == False:
                result = self.__command.execute(parameter, None)
                if result == False:
                    self.log.error('Control command "{0}" not supported with parameter "{1}"'.format(command, parameter))
                    self.mqtt.publish('Unknown command "{0}"'.format(command))
            if result == True:
                self.mqtt.publish('debug/commandresult', 'Success')
        except CommandException as e:
            self.log.warning(e)
            self.mqtt.publish('debug/commandresult ', str(e))
        except Exception as e:
            self.log.error(e)

    def new_cast_status(self, status):
        self.log.info(status)
        self.status.setCastState(status)
        self.__mqtt_publish(self.status)

    def new_media_status(self, status):
        self.log.info(status)
        self.status.setMediaState(status)
        self.__mqtt_publish(self.status)
        if self.status.state == 'PLAYING':
            # Netflix is not reporting nicely on play / pause state changes, so we poll it to get an up to date status
            if self.status.app == 'Netflix':
                sleep(1)
                self.device.media_controller.update_status()

    def __mqtt_publish(self, msg: ChromeState):
        media = msg.media_json
        state = msg.state_json
        if (self.last_media != media):            
            # Only send new update, if title or state has changed.
            self.mqtt.publish(self.mqttpath + '/media', media, retain = True )
            self.last_media = media
        if (self.last_state != state):
            self.mqtt.publish(self.mqttpath + '/capabilities', state, retain = True )
            self.mqtt.publish(self.mqttpath + '/state', msg.state, retain = True )
            self.mqtt.publish(self.mqttpath + '/volume', msg.volume, retain = True )
            self.mqtt.publish(self.mqttpath + '/app', msg.app, retain=True)
            self.last_state = state

    def shutdown(self):
        self.mqtt.publish(self.mqttpath + '/capabilities', None, retain=False)
        self.mqtt.publish(self.mqttpath + '/media', None, retain=False)
        self.mqtt.publish(self.mqttpath + '/state', None, retain=False)
        self.mqtt.publish(self.mqttpath + '/volume', None, retain=False)
        self.mqtt.publish(self.mqttpath + '/app', None, retain=False)
