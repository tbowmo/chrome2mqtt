from pychromecast import Chromecast
from chrome2mqtt.chromestate import ChromeState
from enum import Enum
import logging
import sys
import json
from inspect import signature
from types import SimpleNamespace as Namespace
from pychromecast.controllers.youtube import YouTubeController

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
        self.youtube = YouTubeController()
        self.device.register_handler(self.youtube)

    def execute(self, cmd, payload) -> CommandResult:
        """execute command on the chromecast
        
        Arguments:
            cmd {[string]}
            payload {[string]}
        
        Returns:
            CommandResult -- result object from the command execution
        """
        method=getattr(self, cmd, lambda x : False)
        sig = signature(method)
        try:
            result = False
            if len(sig.parameters) == 0:
                result = method()
            else:
                result = method(payload)
            if result == True:
                return CommandResult(CommandResult.Result.Success)
            elif result == False:
                return CommandResult(CommandResult.Result.NoCommand)
            return CommandResult(CommandResult.Result.WrongUse, result)
        except:
            self.log.error('Unexpected error : ', sys.exc_info())
            return CommandResult(CommandResult.Result.Failed, sys.exc_info()[0])

    def stop(self):
        """ Stop playing on the chromecast """
        self.device.media_controller.stop()
        self.status.clear()
        return True

    def pause(self):
        """ Pause playback """
        self.device.media_controller.pause()
        return True

    def fwd(self):
        self.log.warn('fwd is a deprecated function, use next instead')
        return self.next(payload)

    def next(self):
        """ Skip to next track """
        self.device.media_controller.queue_next()
        return True
        
    def rev(self):
        self.log.warn('rev is a deprecated function, use prev instead')
        return self.prev(payload)

        """ Rewind to previous track """
        self.device.media_controller.queue_prev()
        return True

    def quit(self):
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
            mediaObj = "Failed"
            try:
                mediaObj = json.loads(media, object_hook=lambda d: Namespace(**d))
            except:
                return "Seems that {0} isn't a valid json objct".format(media)
            if hasattr(mediaObj, 'link') and hasattr(mediaObj, 'type'):
                if mediaObj.type.lower() == 'youtube':
                    self.youtube.play_video(mediaObj.link)
                else:
                    self.device.media_controller.play_media(mediaObj.link, mediaObj.type)
            else:
                return 'Wrong patameter, it should be json object with: {{link: string, type: string}}, you sent {0}'.format(media)
        return True

    def volume(self, level):
        """ Set the volume level """
        if level is None or level == '':
            return 'You need to specify volume level'
        self.device.set_volume(int(level) / 100.0)
        return True

    def mute(self, mute):
        """ Mute device """
        mute = mute.lower()
        if (mute is None or mute == ''):
            self.device.set_volume_muted(not self.status.muted)
        elif (mute == '1' or mute == 'true'):
            self.device.set_volume_muted(True)
        elif (mute == '0' or mute == 'false'):
            self.device.set_volume_muted(False)
        else:
            return 'mute could not match "{0}" as a parameter'.format(mute)
        return True
