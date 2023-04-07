'''
Handles events from a chromecast device, and reports these to various endpoints
'''
from time import sleep
import logging
from typing import Callable
from attrs import define, field
from pychromecast import Chromecast
from .command import Command, CommandException
from .chromestate import ChromeState

@define
class ChromeEvent:
    '''
        Handle events to and from registered chromecast devices.

        Internally it listens for new media and / or cast messages from
        the chromecast it handles. and calls the callback specified in order
        to update status.

        Also handles actions destined for the specific device, by calling
        the action method
    '''
    #pylint: disable=no-member
    device: Chromecast = field()
    status: ChromeState = field()
    callback: Callable[[ChromeState, str], None] =  field(default = None)
    name: str = field(default=None)
    __log: logging.Logger = field(init=False, default = None)
    __command: Command = field(init=False, default = None)

    def __attrs_post_init__(self):
        self.__log = logging.getLogger(f'chromevent_{self.device.cast_type}_{self.name}')

        self.device.register_status_listener(self)
        self.device.media_controller.register_status_listener(self)

        self.device.wait()
        self.__command = Command(self.device, self.status)

    def action(self, command, parameter):
        ''' Handle action to the chromecast device '''
        try:
            result = self.__command.execute(command, parameter)
            if not result:
                self.__log.error(
                    'Command "%s" not supported with parameter "%s"',
                    command,
                    parameter
                )
            if result:
                self.__log.info('Success')
        except CommandException as exception:
            self.__log.warning(exception)
        except Exception as exception: #pylint: disable=broad-except
            self.__log.error(command)
            self.__log.error(parameter)
            self.__log.error(exception)

    def new_cast_status(self, status):
        ''' Receives updates when new app is starting on the chromecast '''
        self.__log.info(status)
        self.status.set_cast_state(status)
        self.__callback(self.status)

    def new_media_status(self, status):
        ''' Receives updates when new media changes is happening '''
        self.__log.info(status)
        self.status.set_media_state(status)
        self.__callback(self.status)
        if self.status.state == 'PLAYING' and self.status.app == 'Netflix':
            # Netflix is not reporting nicely on play / pause state changes,
            # so we poll it to get an up to date status
            sleep(1)
            self.device.media_controller.update_status()

    def __callback(self, msg: ChromeState):
        if self.callback is not None:
            self.callback(msg, self.name) #pylint: disable=not-callable
