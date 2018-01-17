#!/usr/bin/python3
import bottle
import pychromecast
import time
import json
from chromeevent import ChromeStatusUpdater
import api
from streams import streams

# Using IP address, rather than name, speeds up the startup of the program
casts = pychromecast.get_chromecasts()
if len(casts) == 0:
    print("No Devices Found")
    exit()
if (casts[0].cast_type == "audio"):
    audio = casts[0] #pychromecast.Chromecast('chromecastaudio') #get_chromecast(friendly_name="Chrome Audio Stuen")
    video = casts[1] #pychromecast.Chromecast('chromecastvideo') #get_chromecast(friendly_name="Chrome TV Stuen")
else:
    audio = casts[1]
    video = casts[0]

print(audio.cast_type)
print(video.cast_type)

    
audio.wait()
video.wait()

api.casters = {
    'video' : ChromeStatusUpdater(video,156, streams),
    'audio' : ChromeStatusUpdater(audio,157, streams)
    }    


app = application = bottle.default_app()



if __name__ == "__main__":
    app.run(port=8181)


