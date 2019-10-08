from pychromecast import Chromecast
from chrome2mqtt.chromestate import ChromeState
from enum import Enum
import logging
import sys
import json

class CommandResult:
    class Result(Enum):
        """
        Result enum for command execution
        """
        Success = 1
        Failed = 2
        WrongUse = 3
        NoCommand = 4

    
    @property
    def result(self):
        return self.__result
    
    @property
    def error(self):
        return self.__error

    def __init__(self, result = None, error = None):
        if (result is None):
            result = self.Result.Failed
        self.__result = result
        self.__error = error

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
        method=getattr(self, cmd, lambda x : False)

        try:
            result = method(payload)
            if result == True:
                return CommandResult(CommandResult.Result.Success)
            elif result == False:
                return CommandResult(CommandResult.Result.NoCommand)
            return CommandResult(CommandResult.Result.WrongUse, result)
        except:
            self.log.error('Unexpected error : ', sys.exc_info())
            return CommandResult(CommandResult.Result.Failed, sys.exc_info()[0])

    def stop(self, payload = None):
        """ Stop playing on the chromecast """
        self.device.media_controller.stop()
        self.status.clear()
        return True

    def pause(self, payload = None):
        """ Pause playback """
        self.device.media_controller.pause()
        return 'Test'

    def fwd(self, payload = None):
        self.log.warn('fwd is a deprecated function, use next instead')
        return self.next(payload)

    def next(self, payload = None):
        """ Skip to next track """
        self.device.media_controller.queue_next()
        return True
        
    def rev(self, payload = None):
        self.log.warn('rev is a deprecated function, use prev instead')
        return self.prev(payload)

    def prev(self, payload = None):
        """ Rewind to previous track """
        self.device.media_controller.queue_prev()
        return True

    def quit(self, payload = None):
        """ Quit running application on chromecast """
        self.device.media_controller.stop()
        self.device.quit_app
        self.status.clear()
        return True

    def play(self, media=None):
        """ Play a media URL on the chromecast """
        if media is None or media == '':
            self.device.media_controller.play()
        else:
            media = json.loads(media)
            if hasattr(media, 'link') and hasattr(media, 'type'):
                self.device.media_controller.play_media(media.link, media.type)
            else:
                return 'Wrong media type, should be json: {link: string, type: string}'
        return True

    def volume(self, level):
        """ Set the volume level """
        if level is None or level == '':
            return 'You need to specify volume level'
        self.device.set_volume(int(level) / 100.0)
        return True

    def mute(self, p):
        """ Mute device """
        p = p.lower()
        if (p == '' or p == None):
            self.device.set_volume_muted(not self.status.muted)
        elif (p == '1' or p == 'true'):
            self.device.set_volume_muted(True)
        elif (p == '0' or p == 'false'):
            self.device.set_volume_muted(False)
        else:
            print('no match')
        return True
