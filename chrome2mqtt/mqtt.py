''' Internal MQTT handler for the project '''
import logging
from time import sleep
from datetime import datetime
import paho.mqtt.client as mqtt

class MQTT(mqtt.Client):
    """ Mqtt handler, takes care of adding a root topic to all topics
        managed by this class, so others do not have to be aware of
        this root topic
    """

    is_connected = False
    root = ''

    def __init__(self, host='127.0.0.1', port=1883, client='chrome', root='', user=None, password=None): #pylint: disable=too-many-arguments, line-too-long
        super().__init__(host, port)
        self.subscriptions = []
        self.host = host
        self.port = int(port)
        if root != '':
            self.root = root + '/'
        self.log = logging.getLogger('mqtt')
        self._client_id = client
        if user is not None:
            self.username_pw_set(user, password)
        self.connect()

    def subscribe(self, topic, qos=0):
        ''' subscribe to a topi '''
        if topic not in self.subscriptions:
            self.subscriptions.append(topic)
        topic = self.root + topic
        self.log.info('subscribing - %s : %s', topic, len(self.subscriptions))
        super().subscribe(topic, qos)

    def message_callback_add(self, topic, callback):
        ''' Add message callbacks, is called when a message matching topic is received '''
        topic = self.root + topic
        super().message_callback_add(topic, callback)

    def publish(self, topic, payload=None, qos=0, retain=False):
        ''' publish on mqtt, adding root topic to the topic '''
        topic = self.root + topic
        if self.is_connected:
            super().publish(topic, payload, qos, retain)

    def on_connect(self, mqttc, obj, flags, rc): # pylint: disable=unused-argument, invalid-name
        ''' handle connection established '''
        self.log.warning('Connect %s', rc)
        if rc == 0:
            self.is_connected = True
            self.publish('debug/lastconnect', datetime.now().strftime('%c'), retain=True)
            for subscription in self.subscriptions:
                self.subscribe(subscription)
        else:
            raise Exception('Connection failed')

    def on_disconnect(self, client, userdata, rc): # pylint: disable=unused-argument, invalid-name
        ''' handle disconnects '''
        self.log.warning('Disconnected, reconnecting')
        self.publish('debug/lastdisconnect', datetime.now().strftime('%c'), retain=True)
        self.is_connected = False
        self.reconnect()

    def on_log(self, mqttc, obj, level, buf): # pylint: disable=unused-argument
        ''' Log handler function '''
        self.log.debug(buf)

    def connnect(self):
        ''' Connect to the mqtt broker '''
        self.connect(self.host, self.port, 30)
        self.loop_start()
        while not self.is_connected:
            sleep(1)
            self.log.info('Waiting for connection to %s', self.host)
