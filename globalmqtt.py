"""
    MQTT topic for global commands (quit / pause / stop), sends the same cmd to all known chromecasts
"""

from mqtt import MQTT
import logging

class GlobalMQTT:

    def __init__(self, casters, mqtt:MQTT):
        self.casters = casters
        controlPath = 'control'
        mqtt.subscribe(controlPath)
        mqtt.message_callback_add(controlPath, self.mqtt_action)
        self.log = logging.getLogger('mqttglobal')
        
    def mqtt_action(self, client, userdata, message):
        p = message.payload.decode("utf-8")
        for c in self.casters.keys():
            self.log.warn('GlobalMQTT sending ' + p + ' to ' + c)
            caster = self.casters[c]
            if p == 'quit':
                caster.quit()
            if p == 'pause':
                caster.pause()
            if p == 'stop':
                cater.stop()
