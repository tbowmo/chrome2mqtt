"""
    Handles events from a chromecast device, and reports these to various endpoints
"""

class GlobalControl:

    def __init__(self, casters, mqtt, mqttroot):
        self.casters = casters
        self.mqtt = mqtt
        controlPath = mqttroot + '/control'
        self.mqtt.subscribe(controlPath)
        self.mqtt.message_callback_add(controlPath, self.mqtt_action)
        
    def mqtt_action(self, client, userdata, message):
        p = message.payload
        print(p)
        if p == b'quit':
            for c in self.casters:
                c.quit()
        if p == b'pause':
            for c in self.casters:
                c.pause()
        if p == b'stop':
            for c in self.casters:
                c.stop()
