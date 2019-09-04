import paho.mqtt.client as mqtt
import logging

class MQTT(mqtt.Client):
    def __init__(self, host='127.0.0.1', port=1883, client='chrome'):
        super().__init__(host, port)
        self.subscriptions = []
        self.host = host
        self.port = port
        self.log = logging.getLogger('mqtt')
        self._client_id=client

    def on_connect(self, mqttc, obj, flags, rc):
        for s in self.subscriptions:
            self.subscribe(s)

    def on_publish(self, mqttc, obj, mid):
        pass

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        self.log.info("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        self.log.debug(string)

    def conn(self):
        self.connect(self.host, self.port, 60)

    def run(self):
        self.subscribe("$SYS/#", 0)

        rc = 0
        while rc == 0:
            rc = self.loop()
        return rc
