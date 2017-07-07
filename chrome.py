#!/usr/bin/python3
import bottle
from bottle import request, response
from bottle import get
import pychromecast
import time
import json
from chromeevent import ChromeStatusUpdater
from streams import streams

# Using IP address, rather than name, speeds up the startup of the program
audio = pychromecast.Chromecast('Chromecast-Audio') #get_chromecast(friendly_name="Chrome Audio Stuen")
audio.wait()

video = pychromecast.Chromecast('Chromecast') #get_chromecast(friendly_name="Chrome TV Stuen")
video.wait()

casters = {
  'video' : ChromeStatusUpdater(video,156, streams),
  'audio' : ChromeStatusUpdater(audio,157, streams)
  }  


app = application = bottle.default_app()


@get('/<device>/list')
def medialist(device):
  od = casters[device].getChannelList()
  return json.dumps(od, default=lambda o: o.__dict__)
    
@get('/')
def listplayers():
  return json.dumps(list(casters.keys()));
    
@get('/<device>')
def getdevicestatus(device):
  if (device == 'favicon.ico'):
    return
  m = casters[device]
  return m.state_json()

@get('/<device>/<command>')     
def control_player(device, command):
  player = casters[device]
  if command == 'pause':
    player.pause()
  elif command == 'play':
    player.play()
  elif command == 'skip':
    player.skip()
  elif command == 'stop':
    player.stop()
  elif command == 'quit':
    player.quit()
  time.sleep(0.5)
  return player.state_json()

@get('/<device>/play/<media>')
def play_media(device, media):
  player = casters[device]
  player.play(media)
  time.sleep(1)
  return player.state_json()

@get('/status')
def status():
  player = casters['video']
  if player.status.chromeApp != "Backdrop":
    return player.state_json();
  else:
    player = casters['audio']
    return player.state_json();

if __name__ == "__main__":
  app.run(host='192.168.0.64', port=8182)


