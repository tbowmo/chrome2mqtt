#!/usr/bin/python3
"""
    Program that handles chromecast integration, mainly with domoticz. But also implements
    a crude rest api for controlling a chromecast, and start streaming pre-defined streams.

    This can be used to create a web interface for controlling a chromecast (for example in
    angular)

    Copyright 2018: Thomas Bowman Mørch
"""
import json
from shutil import copyfile
import bottle
import pychromecast
import api
from chromeevent import ChromeEvent
from streamdata import StreamData, Stream
from bottle import response
from os import environ
from mqtt import MQTT

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

STREAMS = StreamData()
CASTS = pychromecast.get_chromecasts()

if len(CASTS) == 0:
    print("No Devices Found")
    exit()
if CASTS[0].cast_type == "audio":
    AUDIO = CASTS[0]
    VIDEO = CASTS[1]
else:
    AUDIO = CASTS[1]
    VIDEO = CASTS[0]

AUDIO.wait()
VIDEO.wait()

try:
    with open('/config/streams.json') as streams_json:
        stdict = json.loads(streams_json.read())
        for st in stdict:
            STREAMS.add_channel(Stream(**st))
except IOError:
    copyfile('streams.json', '/config/streams.json')

api.casters = {
    'video' : ChromeEvent(VIDEO, STREAMS, mqtt, mqtt_root),
    'audio' : ChromeEvent(AUDIO, STREAMS, mqtt, mqtt_root)
    }


class EnableCors(object):
    name = 'enable_cors'
    api = 2
    cors_host = environ.get('CORS_HOST')
    if not cors_host:
        cors_host = '*'
    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = cors_host
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if bottle.request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors

APP = application = bottle.default_app()
application.install(EnableCors())
if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=8181)
