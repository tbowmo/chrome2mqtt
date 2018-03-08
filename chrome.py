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

APP = application = bottle.default_app()

if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=8181)
