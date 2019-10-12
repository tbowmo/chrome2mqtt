from pychromecast import Chromecast
from chrome2mqtt.chromestate import ChromeState
from enum import Enum
import logging
import sys
import json
from inspect import signature
from types import SimpleNamespace as Namespace
from pychromecast.controllers.youtube import YouTubeController

class Status(Enum):
    """
    Status enum for command execution
    """
    Success = 1
    Failed = 2
    WrongUse = 3
    NoCommand = 4

class Result:

    @property
    def status(self):
        return self.__status
    
    @property
    def error(self):
        return self.__error

    def __init__(self, status = Status.Failed, error = None):
        self.__status = status
        self.__error = error


class CommandError(Exception):
    pass

class Command:
    """
    Class that handles dispatching of commands to a chromecast device   
    """
    def __init__(self, device: Chromecast, status: ChromeState):
        self.device = device
        self.status = status
        self.log = logging.getLogger('Command_' + self.device.name)
        self.youtube = YouTubeController()
        self.device.register_handler(self.youtube)

    def execute(self, cmd, payload) -> Result:
        """execute command on the chromecast
        
        Arguments:
            cmd {[string]}
            payload {[string]}
        
        Returns:
            Result -- result object from the command execution
        """
        method=getattr(self, cmd, lambda x : False)
        sig = signature(method)
        if str(sig) == '(x)':
            return Result(Status.NoCommand)

        try:
            if len(sig.parameters) == 0:
                method()
            else:
                method(payload)
            return Result(Status.Success)
        except CommandError as e:
            self.log.warning(str(e))
            return Result(Status.WrongUse, str(e))
        except Exception as e:
            self.log.error('Unexpected error : ', str(e))
            return Result(Status.Failed, e)

    def stop(self):
        """ Stop playing on the chromecast """
        self.device.media_controller.stop()
        self.status.clear()

    def pause(self):
        """ Pause playback """
        self.device.media_controller.pause()

    def fwd(self):
        self.log.warn('fwd is a deprecated function, use next instead')
        return self.next(payload)

    def next(self):
        """ Skip to next track """
        self.device.media_controller.queue_next()
        
    def rev(self):
        self.log.warn('rev is a deprecated function, use prev instead')
        return self.prev(payload)

        """ Rewind to previous track """
        self.device.media_controller.queue_prev()

    def quit(self):
        """ Quit running application on chromecast """
        self.device.media_controller.stop()
        self.device.quit_app
        self.status.clear()

    def play(self, media=None):
        """ Play a media URL on the chromecast """
        if media is None or media == '':
            self.device.media_controller.play()
        else:
            mediaObj = "Failed"
            try:
                mediaObj = json.loads(media, object_hook=lambda d: Namespace(**d))
            except:
                raise CommandError("Seems that {0} isn't a valid json objct".format(media))
            if hasattr(mediaObj, 'link') and hasattr(mediaObj, 'type'):
                if mediaObj.type.lower() == 'youtube':
                    self.youtube.play_video(mediaObj.link)
                else:
                    self.device.media_controller.play_media(mediaObj.link, mediaObj.type)
            else:
                raise CommandError('Wrong patameter, it should be json object with: {{link: string, type: string}}, you sent {0}'.format(media))

    def volume(self, level):
        """ Set the volume level """
        if level is None or level == '':
            raise CommandError('You need to specify volume level')
        self.device.set_volume(int(level) / 100.0)

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
            raise CommandError('Mute could not match "{0}" as a parameter'.format(mute))
