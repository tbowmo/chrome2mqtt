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
    'video' : ChromeEvent(VIDEO, STREAMS),
    'audio' : ChromeEvent(AUDIO, STREAMS)
    }


class EnableCors(object):
    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = environ['CORS_HOST']
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
