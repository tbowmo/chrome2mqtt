#!/usr/bin/python3
"""
    Program that handles chromecast integration, mainly with domoticz. But also implements
    a crude rest api for controlling a chromecast, and start streaming pre-defined streams.

    This can be used to create a web interface for controlling a chromecast (for example in
    angular)

    Copyright 2018: Thomas Bowman Mørch
"""
from shutil import copyfile
import pychromecast
from chromeevent import ChromeEvent
from os import environ
from mqtt import MQTT
from time import sleep

mqtt_root = environ.get('MQTT_ROOT')
mqtt_host = environ.get('MQTT_HOST')
mqtt_port = environ.get('MQTT_PORT')

if not mqtt_root:
    mqtt_root='chromecast'
if not mqtt_host:
    mqtt_host = '127.0.0.1'
if not mqtt_port:
    mqtt_port = 1883

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

if __name__ == '__main__':
    while True:
        sleep(1)
