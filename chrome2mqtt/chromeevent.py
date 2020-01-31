from time import sleep
from chrome2mqtt.chromestate import ChromeState
from os import path
import logging
from pychromecast import Chromecast
from chrome2mqtt.command import Command, CommandException

class ChromeEvent:
    """ 
        Handles events from a chromecast device, and reports these to various endpoints
    """
    device: Chromecast = None
    last_media = None
    last_state = None
    callback = None
    def __init__(self, device: Chromecast, status: ChromeState, callback = None, name = None):
        self.callback = callback
        self.device = device
        self.name = name
        self.log = logging.getLogger('chromevent_{0}_{1}'.format(self.device.cast_type, self.name))

        self.device.register_status_listener(self)
        self.device.media_controller.register_status_listener(self)

        self.status = status
        
        self.device.wait()
        self.__command = Command(self.device, self.status)

    def action(self, command, parameter):
        try:
            if command == 'ping':
                self.__callback(self.status)
                return
            result = self.__command.execute(command, parameter)
            if result == False:
                result = self.__command.execute(parameter, None)
                if result == False:
                    self.log.error('Control command "{0}" not supported with parameter "{1}"'.format(command, parameter))
            if result == True:
                self.log.info('Success')
        except CommandException as e:
            self.log.warning(e)
        except Exception as e:
            self.log.error(e)

    def new_cast_status(self, status):
        self.log.info(status)
        self.status.setCastState(status)
        self.__callback(self.status)

    def new_media_status(self, status):
        self.log.info(status)
        self.status.setMediaState(status)
        self.__callback(self.status)
        if self.status.state == 'PLAYING':
            # Netflix is not reporting nicely on play / pause state changes, so we poll it to get an up to date status
            if self.status.app == 'Netflix':
                sleep(1)
                self.device.media_controller.update_status()

    def __callback(self, msg: ChromeState):
        if self.callback is not None:
            self.callback(msg, self.name)
