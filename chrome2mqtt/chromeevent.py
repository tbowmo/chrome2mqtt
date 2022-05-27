'''
Handles events from a chromecast device, and reports these to various endpoints
'''
from time import sleep
import logging
from pychromecast import Chromecast
from chrome2mqtt.command import Command, CommandException
from chrome2mqtt.chromestate import ChromeState

class ChromeEvent:
    '''
        Handle events to and from registered chromecast devices.

        Internally it listens for new media and / or cast messages from
        the chromecast it handles. and calls the callback specified in order
        to update status.

        Also handles actions destined for the specific device, by calling
        the action method
    '''
    device: Chromecast = None
    last_media = None
    last_state = None
    callback = None
    def __init__(self, device: Chromecast, status: ChromeState, callback=None, name=None):
        self.callback = callback
        self.device = device
        self.name = name
        self.log = logging.getLogger(f'chromevent_{self.device.cast_type}_{self.name}')

        self.device.register_status_listener(self)
        self.device.media_controller.register_status_listener(self)

        self.status = status

        self.device.wait()
        self.__command = Command(self.device, self.status)

    def action(self, command, parameter):
        ''' Handle action to the chromecast device '''
        try:
            result = self.__command.execute(command, parameter)
            if not result:
                self.log.error('Command "%s" not supported with parameter "%s"', command, parameter)
            if result:
                self.log.info('Success')
        except CommandException as exception:
            self.log.warning(exception)
        except Exception as exception: #pylint: disable=broad-except
            self.log.error(command)
            self.log.error(parameter)
            self.log.error(exception)

    def new_cast_status(self, status):
        ''' Receives updates when new app is starting on the chromecast '''
        self.log.info(status)
        self.status.set_cast_state(status)
        self.__callback(self.status)

    def new_media_status(self, status):
        ''' Receives updates when new media changes is happening '''
        self.log.info(status)
        self.status.set_media_state(status)
        self.__callback(self.status)
        if self.status.state == 'PLAYING' and self.status.app == 'Netflix':
            # Netflix is not reporting nicely on play / pause state changes,
            # so we poll it to get an up to date status
            sleep(1)
            self.device.media_controller.update_status()

    def __callback(self, msg: ChromeState):
        if self.callback is not None:
            self.callback(msg, self.name)
