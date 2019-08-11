#!/usr/bin/python3
"""
    Program that handles chromecast integration to mqtt. 

    Copyright 2018: Thomas Bowman Mørch
"""
from shutil import copyfile
import pychromecast
from globalmqtt import GlobalMQTT
from chromeevent import ChromeEvent
from os import environ
from mqtt import MQTT
from time import sleep, gmtime, strftime
from datetime import datetime

mqtt_root = environ.get('MQTT_ROOT')
mqtt_host = environ.get('MQTT_HOST')
mqtt_port = environ.get('MQTT_PORT')

if not mqtt_root:
    mqtt_root='chromecast'
if not mqtt_host:
    mqtt_host = '127.0.0.1'
if not mqtt_port:
    mqtt_port = 1883
mqtt_port = int(mqtt_port)
mqtt = MQTT(mqtt_host, mqtt_port)
mqtt.conn()
mqtt.loop_start()

CASTS = pychromecast.get_chromecasts()

if len(CASTS) == 0:
    print("No Devices Found")
    exit()

casters = []
for c in CASTS:
    c.wait()
    casters.append(ChromeEvent(c, mqtt, mqtt_root))

gControl = GlobalMQTT(casters, mqtt, mqtt_root)


mqtt.publish(mqtt_root + '/start', datetime.now().strftime('%c'), retain=True)

if __name__ == '__main__':
    while True:
        sleep(1)
