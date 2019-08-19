"""
    MQTT topic for global commands (quit / pause / stop), to send the same cmd to all known chromecasts
"""

class GlobalMQTT:

    def __init__(self, casters, mqtt, mqttroot):
        self.casters = casters
        self.mqtt = mqtt
        controlPath = mqttroot + '/control'
        self.mqtt.subscribe(controlPath)
        self.mqtt.message_callback_add(controlPath, self.mqtt_action)
        
    def mqtt_action(self, client, userdata, message):
        p = message.payload
        if p == b'quit':
            for c in self.casters:
                c.quit()
        if p == b'pause':
            for c in self.casters:
                c.pause()
        if p == b'stop':
            for c in self.casters:
                c.stop()
