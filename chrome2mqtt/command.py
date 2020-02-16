'''
Handles command dispatching for chomecast devices, use the Command class
'''
from inspect import signature
from types import SimpleNamespace as Namespace
import json
import logging
from time import sleep
from pychromecast import Chromecast
from pychromecast.controllers.youtube import YouTubeController
from chrome2mqtt.chromestate import ChromeState

class CommandException(Exception):
    """
    Exception class for command errors
    """

class Command:
    """
    Class that handles dispatching of commands to a chromecast device
    """
    def __init__(self, device: Chromecast, status: ChromeState):
        self.chromestate = status
        self.device = device
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
        method = getattr(self, cmd, lambda x: False)
        sig = signature(method)
        if str(sig) == '(x)':
            return False

        if sig.parameters:
            method()
        else:
            method(payload)
        return True

    def stop(self):
        """ Stop playing on the chromecast """
        self.device.media_controller.stop()

    def pause(self, pause):
        """ Pause playback """
        if (pause is None or pause == ''):
            if self.device.media_controller.is_paused:
                self.device.media_controller.play()
            else:
                self.device.media_controller.pause()
        else:
            pause = str(pause).lower()
            if pause in ('1', 'true'):
                self.device.media_controller.pause()
            elif pause in ('0', 'false'):
                self.device.media_controller.play()
            else:
                raise CommandException('Pause could not match "{0}" as a parameter'.format(pause))

    def fwd(self):
        """ Skip to next track """
        self.log.warning('fwd is a deprecated function, use next instead')
        return self.next()

    def rev(self):
        """ Rewind to previous track """
        self.log.warning('rev is a deprecated function, use prev instead')
        return self.prev()

    def next(self):
        """ Skip to next track """
        self.device.media_controller.queue_next()

    def prev(self):
        """ Rewind to previous track """
        self.device.media_controller.queue_prev()

    def quit(self):
        """ Quit running application on chromecast """
        self.chromestate.clear()
        self.device.quit_app()

    def play(self, media=None):
        """ Play a media URL on the chromecast """
        if media is None or media == '':
            self.device.media_controller.play()
        else:
            media_obj = "Failed"
            try:
                media_obj = json.loads(media, object_hook=lambda d: Namespace(**d))
            except:
                raise CommandException("Seems that {0} isn't a valid json object".format(media))
            if hasattr(media_obj, 'link') and hasattr(media_obj, 'type'):
                i = 1
                while True:
                    if media_obj.type.lower() == 'youtube':
                        self.youtube.play_video(media_obj.link)
                    else:
                        self.device.media_controller.play_media(media_obj.link, media_obj.type)
                    sleep(0.5)
                    if self.device.media_controller.is_playing or i > 3:
                        break
                    i = i + 1
            else:
                raise CommandException(
                    'Wrong parameter, it should be json object with: {{link: string, type: string}}, you sent {0}'.format(media) #pylint: disable=line-too-long
                    )

    def volume(self, level):
        """ Set the volume level """
        if level is None or level == '':
            raise CommandException('You need to specify volume level')
        if int(level) > 100:
            level = 100
        if int(level) < 0:
            level = 0
        self.device.set_volume(int(level) / 100.0)

    def mute(self, mute):
        """ Mute device """
        if (mute is None or mute == ''):
            self.device.set_volume_muted(not self.device.status.volume_muted)
        else:
            mute = str(mute).lower()
            if mute in ('1', 'true'):
                self.device.set_volume_muted(True)
            elif mute in ('0', 'false'):
                self.device.set_volume_muted(False)
            else:
                raise CommandException('Mute could not match "{0}" as a parameter'.format(mute))
