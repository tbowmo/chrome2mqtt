import paho.mqtt.client as mqtt

class MQTT(mqtt.Client):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.subscriptions = []
        self.host = host
        self.port = port

    def on_connect(self, mqttc, obj, flags, rc):
        for s in self.subscriptions:
            self.subscribe(s)
        print("rc: "+str(rc))

    def on_publish(self, mqttc, obj, mid):
        print("mid: " + str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)

    def conn(self):
        self.connect(self.host, self.port, 60)

    def run(self):
        #self.connect("m2m.eclipse.org", 1883, 60)
        self.subscribe("$SYS/#", 0)

        rc = 0
        while rc == 0:
            rc = self.loop()
        return rc
