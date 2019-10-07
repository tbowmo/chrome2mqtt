from chrome2mqtt.mqtt import MQTT
import logging
from os import path

class GlobalMQTT:
    """
        MQTT topic handler for global commands (quit / pause / stop), sends the same cmd to all known chromecasts
    """

    def __init__(self, casters, mqtt:MQTT):
        self.casters = casters
        controlPath = 'control/#'
        mqtt.subscribe(controlPath)
        mqtt.message_callback_add(controlPath, self.mqtt_action)
        self.log = logging.getLogger('mqttglobal')
        
    def mqtt_action(self, client, userdata, message):
        p = message.payload.decode("utf-8")
        cmd = path.basename(path.normpath(message.topic))
        for c in self.casters.keys():
            caster = self.casters[c]
            if cmd == 'volume':
                caster.volume(p)
            elif cmd == 'mute':
                caster.mute(p)
            else:
                if p == 'quit':
                    caster.quit()
                if p == 'pause':
                    caster.pause()
                if p == 'stop':
                    caster.stop()
