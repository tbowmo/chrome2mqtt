from pychromecast import Chromecast
from chrome2mqtt.chromestate import ChromeState
from enum import Enum
import logging
import sys

class CommandResult(Enum):
    """
    Result enum for command execution
    """
    Success = 1
    Failed = 2
    NoCommand = 3

class Command:
    """
    Class that handles dispatching of commands to a chromecast device   
    """
    def __init__(self, device: Chromecast, status: ChromeState):
        self.device = device
        self.status = status
        self.log = logging.getLogger('Command_' + self.device.cast_type)

    def execute(self, cmd, payload) -> CommandResult:
        """execute command on the chromecast
        
        Arguments:
            cmd {[string]}
            payload {[string]}
        
        Returns:
            CommandResult -- Enum that describes how the execution went
        """
        method=getattr(self,cmd,lambda x : False)
        print('----------------------------')
        result = method(payload)
        if result == False:
            return CommandResult.NoCommand
        if result == None:
            return CommandResult.Failed
        return CommandResult.Success

    def stop(self, payload = None):
        """ Stop playing on the chromecast """
        try:
            self.device.media_controller.stop()
            self.status.clear()
            return True
        except:
            self.__handle_error()

    def pause(self, payload = None):
        """ Pause playback """
        try:
            self.device.media_controller.pause()
            return True
        except:
            self.__handle_error() 
    def fwd(self, payload = None):
        self.log.warn('fwd is a deprecated function, use next instead')
        return self.next(payload)

    def next(self, payload = None):
        """ Skip to next track """
        try:
            self.device.media_controller.queue_next()
            return True
        except:
            self.__handle_error()

    def rev(self, payload = None):
        self.log.warn('rev is a deprecated function, use prev instead')
        return self.prev(payload)

    def prev(self, payload = None):
        """ Rewind to previous track """
        try: 
            self.device.media_controller.queue_prev()
            return True
        except:
            self.__handle_error()

    def quit(self, payload = None):
        """ Quit running application on chromecast """
        try:
            self.device.media_controller.stop()
            self.device.quit_app
            self.status.clear()
            return True
        except:
            self.__handle_error()

    def play(self, media=None):
        """ Play a media URL on the chromecast """
        try:
            if media is None:
                self.device.media_controller.play()
            else:
                self.device.media_controller.play_media(media.link, media.media)
            return True
        except:
            self.__handle_error()

    def volume(self, level):
        """ Set the volume level """
        try:
            self.device.set_volume(int(level) / 100.0)
            return True
        except:
            self.__handle_error()

    def mute(self, p):
        p = p.lower()
        try:
            if (p == '' or p == None):
                self.device.set_volume_muted(not self.status.muted)
            elif (p == '1' or p == 'true'):
                self.device.set_volume_muted(True)
            elif (p == '0' or p == 'false'):
                self.device.set_volume_muted(False)
            else:
                print('no match')
            return True
        except:
            self.__handle_error()

    def __handle_error(self):
        self.log.error('Unexpected error : ', sys.exc_info())
