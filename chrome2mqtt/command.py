from chrome2mqtt.chromestate import ChromeState
from inspect import signature
from pychromecast import Chromecast
from pychromecast.controllers.youtube import YouTubeController
from types import SimpleNamespace as Namespace
import json
import logging

class CommandException(Exception):
    """
    Exception class for command errors
    """
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

    def execute(self, cmd, payload):
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
            return False

        if len(sig.parameters) == 0:
            method()
        else:
            method(payload)
        return True

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
                raise CommandException("Seems that {0} isn't a valid json object".format(media))
            if hasattr(mediaObj, 'link') and hasattr(mediaObj, 'type'):
                if mediaObj.type.lower() == 'youtube':
                    self.youtube.play_video(mediaObj.link)
                else:
                    self.device.media_controller.play_media(mediaObj.link, mediaObj.type)
            else:
                raise CommandException('Wrong parameter, it should be json object with: {{link: string, type: string}}, you sent {0}'.format(media))

    def volume(self, level):
        """ Set the volume level """
        if level is None or level == '':
            raise CommandException('You need to specify volume level')
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
            raise CommandException('Mute could not match "{0}" as a parameter'.format(mute))
