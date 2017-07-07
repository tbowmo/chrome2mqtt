#!/usr/bin/python3
import bottle
import pychromecast
import time
import json
from chromeevent import ChromeStatusUpdater
import api
from streams import streams

# Using IP address, rather than name, speeds up the startup of the program
audio = pychromecast.Chromecast('Chromecast-Audio') #get_chromecast(friendly_name="Chrome Audio Stuen")
audio.wait()

video = pychromecast.Chromecast('Chromecast') #get_chromecast(friendly_name="Chrome TV Stuen")
video.wait()

api.casters = {
  'video' : ChromeStatusUpdater(video,156, streams),
  'audio' : ChromeStatusUpdater(audio,157, streams)
  }  


app = application = bottle.default_app()



if __name__ == "__main__":
  app.run(host='192.168.0.64', port=8182)


