import paho.mqtt.client as mqtt
import logging
from time import sleep, strftime
from datetime import datetime

class MQTT(mqtt.Client):
    """ Mqtt handler, takes care of adding a root topic to all topics 
        managed by this class, so others do not have to be aware of
        this root topic
    """
    
    is_connected = False
    root = ''
    def __init__(self, host='127.0.0.1', port=1883, client='chrome', root='', user=None, password=None):
        super().__init__(host, port)
        self.subscriptions = []
        self.host = host
        self.port = int(port)
        if root != '':
            self.root = root + '/'
        self.log = logging.getLogger('mqtt')
        self._client_id=client
        if (user is not None):
            self.username_pw_set(user, password)
        self.conn()

    def subscribe(self, topic, qos=0):
        topic = self.root + topic
        super().subscribe(topic, qos)

    def message_callback_add(self, sub, callback):
        sub = self.root + sub
        super().message_callback_add(sub, callback)

    def publish(self, topic, payload = None, qos = 0, retain=False):
        topic = self.root + topic
        if self.is_connected:
            super().publish(topic, payload, qos, retain)

    def on_connect(self, mqttc, obj, flags, rc):
        if (rc == 0):
            self.is_connected = True
            self.publish('debug/lastconnect',datetime.now().strftime('%c'), retain=True)
            for s in self.subscriptions:
                self.subscribe(s)
        raise Exception('Connection failed')

    def on_disconnect(self, client, userdata, rc):
        self.log.warn("Disconnected, reconnecting")
        self.publish('debug/lastdisconnect',datetime.now().strftime('%c'), retain=True)
        self.is_connected = False
        while not is_connected:
            if not is_connected:
                self.log.warn("Reconnect attempt")
                self.conn()
            sleep(5)

    def on_log(self, mqttc, obj, level, buf):
        self.log.debug(buf)

    def conn(self):
        self.connect(self.host, self.port, 30)
        self.loop_start()
        while not self.is_connected:
            pass
