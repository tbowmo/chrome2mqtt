#!/usr/bin/python3
"""
    Program that handles chromecast integration to mqtt. 

    Copyright 2018: Thomas Bowman Mørch
"""
import pychromecast
from globalmqtt import GlobalMQTT
from chromeevent import ChromeEvent
from os import environ
from mqtt import MQTT
from time import sleep, strftime
from datetime import datetime
import sys
import getopt
import logging

mqtt_root = environ.get('MQTT_ROOT')
mqtt_host = environ.get('MQTT_HOST')
mqtt_port = environ.get('MQTT_PORT')

if not mqtt_root:
    mqtt_root='chromecast'
if not mqtt_host:
    mqtt_host = '127.0.0.1'
if not mqtt_port:
    mqtt_port = 1883

logLevel = logging.DEBUG

def parse_args(argv):
    global mqtt_host, mqtt_port, mqtt_root, logLevel
    try:
        opts, args = getopt.getopt(argv, 'hr:p:m:l:', ['port=', 'root=', 'host=', 'log='])
    except getopt.GetoptError:
        help()
    for opt, arg in opts:
        if opt == '-h':
            help()
        elif opt in('-p','--port'):
            mqtt_port = arg
        elif opt in('-r','--root'):
            mqtt_root = arg
        elif opt in('-m','--host'):
            mqtt_host = arg
        elif opt in('-l','--log'):
            logLevel = int(arg)

def start_banner():
    print('Chromecast2MQTT by tbowmo')
    print('Connecting to mqtt host ' + mqtt_host + ' port ' + str(mqtt_port))
    print('Using mqtt root ' + mqtt_root)

def help():
    print('Help text for Chromecast2MQTT')
    print('command line options')
    print('-r, --root   root topic')
    print('-m, --host   mqtt host')
    print('-p, --port   mqtt port')
    print('-l, --log    minimum loglevel')
    sys.exit(0)

parse_args(sys.argv[1:])

logging.basicConfig(level=logLevel,
                    format = '%(asctime)s %(levelname)-8s %(message)s',
                    handlers = [logging.StreamHandler()])
    
start_banner()
try:
    mqtt_port = int(mqtt_port)
    mqtt = MQTT(mqtt_host, mqtt_port)
    mqtt.conn()
    mqtt.loop_start()
except:
    print('Error connecting to mqtt host ' + mqtt_host + ' on port ' + str(mqtt_port))
    sys.exit(1)

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
