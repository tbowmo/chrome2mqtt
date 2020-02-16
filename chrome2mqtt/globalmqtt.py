'''
Global MQTT handler, than can send the same command to all devices registered
like "STOP" or "QUIT". Can be used to stop all chromecasts playing.
'''
import logging
from os import path
from chrome2mqtt.mqtt import MQTT

class GlobalMQTT: #pylint: disable=too-few-public-methods
    """
        MQTT topic handler for global commands (quit / pause / stop),
        sends the same cmd to all known chromecasts
    """

    def __init__(self, casters, mqtt: MQTT):
        self.casters = casters
        control_path = 'control/#'
        mqtt.message_callback_add(control_path, self.mqtt_action)
        self.log = logging.getLogger('mqttglobal')

    def mqtt_action(self, client, userdata, message): #pylint: disable=unused-argument
        ''' handles action from mqtt topic on all devices registrered '''
        payload = message.payload.decode("utf-8")
        cmd = path.basename(path.normpath(message.topic))
        for cast in self.casters.keys():
            caster = self.casters[cast]
            caster.action(cmd, payload)
