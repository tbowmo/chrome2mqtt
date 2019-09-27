import paho.mqtt.client as mqtt
import logging
from time import sleep, strftime
from datetime import datetime

class MQTT(mqtt.Client):
    is_connected = False
    root = ''
    def __init__(self, host='127.0.0.1', port=1883, client='chrome', root = ''):
        super().__init__(host, port)
        self.subscriptions = []
        self.host = host
        self.port = port
        if root != '':
            self.root = root + '/'
        self.log = logging.getLogger('mqtt')
        self._client_id=client

    def subscribe(self, topic, qos=0):
        super().subscribe(self.root + topic, qos)

    def message_callback_add(self, sub, callback):
        super().message_callback_add(self.root + sub, callback)

    def publish(self, topic, payload = None, qos = 0, retain=False):
        if self.is_connected:
            super().publish(self.root + topic, payload, qos, retain)

    def on_connect(self, mqttc, obj, flags, rc):
        self.is_connected = True
        self.publish('debug/lastconnect',datetime.now().strftime('%c'), retain=True)
        for s in self.subscriptions:
            self.subscribe(s)

    def on_disconnect(self, client, userdata, rc):
        self.log.warn("Disconnected, reconnecting")
        self.publish('debug/lastdisconnect',datetime.now().strftime('%c'), retain=True)
        self.is_connected = False
        while not is_connected:
            if not is_connected:
                self.log.warn("Reconnect attempt")
                self.conn()
            sleep(5)

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        self.log.info("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        self.log.debug(string)

    def conn(self):
        self.connect(self.host, self.port, 30)
        self.loop_start()
        while not self.is_connected:
            pass

    def run(self):
        rc = 0
        while rc == 0:
            rc = self.loop()
        return rc
