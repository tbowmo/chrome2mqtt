#!/usr/bin/python3
import web
import pychromecast
import time
import json
import collections
from chromeevent import ChromeStatusUpdater

channels = {
  'drp3' : {'link':'http://live-icy.gss.dr.dk:80/A/A05H.mp3', 'name':'drp3', 'friendly':'DR P3', 'extra':'Musik'},
  'drp2' : {'link':'http://live-icy.gss.dr.dk:80/A/A04H.mp3', 'name':'drp2', 'friendly':'DR P2', 'extra':'Musik'},
  'drp1' : {'link':'http://live-icy.gss.dr.dk:80/A/A03H.mp3', 'name':'drp1', 'friendly':'DR P1', 'extra':''},
  'drp4' : {'link':'http://live-icy.gss.dr.dk:80/A/A10H.mp3', 'name':'drp4', 'friendly':'DR P4', 'extra':''},
  'drp6' : {'link':'http://live-icy.gss.dr.dk:80/A/A29H.mp3', 'name':'drp6', 'friendly':'DR P6', 'extra':''},
  'drp7' : {'link':'http://live-icy.gss.dr.dk:80/A/A21H.mp3', 'name':'drp7', 'friendly':'DR P7', 'extra':''},
  'ramasjang' : {'link':'http://live-icy.gss.dr.dk:80/A/A24H.mp3', 'name':'ramasjang', 'friendly':'Ramasjang', 'extra':'børn'},
  'nyheder' : {'link':'http://live-icy.gss.dr.dk:80/A/A02H.mp3', 'name':'nyheder', 'friendly':'Nyheder', 'extra':'Nyheder'},
  '80sforever' : {'link':'http://50.7.99.163:11067/256', 'name':'80sforever', 'friendly':'80s','extra':'Musik'},
  '97780s' : {'link':'http://7599.live.streamtheworld.com:80/977_80AAC_SC', 'name':'97780s', 'friendly':'80s 977', 'extra':'Musik'},
  '97790s' : {'link':'http://7599.live.streamtheworld.com:80/977_90AAC_SC', 'name':'97790s', 'friendly':'90s 977', 'extra':'Musik'}
  }
  
urls = (
  '/', 'list_players',
  '/test', 'test',
  '/([a-z]*)', 'get_player',
  '/([a-z]*)/list', 'medialist',
  '/([a-z]*)/play/(.*)', 'play_media',
  '/([a-z]*)/([a-z]*)', 'control_player'
  )

app = web.application(urls, globals())

audio = pychromecast.get_chromecast(friendly_name="Chrome Audio Stuen")
audio.wait()

video = pychromecast.get_chromecast(friendly_name="Chrome TV Stuen")
video.wait()


casters = {
  'video' : ChromeStatusUpdater(video,156),
  'audio' : ChromeStatusUpdater(audio,157)
  }  

casters['audio'].addChannel(link='http://live-icy.gss.dr.dk:80/A/A05H.mp3', friendly = 'DR P3', extra = 'Musik')
casters['audio'].addChannel(link='http://live-icy.gss.dr.dk:80/A/A04H.mp3', friendly = 'DR P2', extra = 'Musik')
casters['audio'].addChannel(link='http://live-icy.gss.dr.dk:80/A/A03H.mp3', friendly='DR P1')
casters['audio'].addChannel(link='http://live-icy.gss.dr.dk:80/A/A10H.mp3', friendly='DR P4')
casters['audio'].addChannel(link='http://live-icy.gss.dr.dk:80/A/A29H.mp3', friendly='DR P6')
casters['audio'].addChannel(link='http://live-icy.gss.dr.dk:80/A/A21H.mp3', friendly='DR P7')
casters['audio'].addChannel(link='http://live-icy.gss.dr.dk:80/A/A24H.mp3', friendly='Ramasjang', extra='børn')
casters['audio'].addChannel(link='http://live-icy.gss.dr.dk:80/A/A02H.mp3', friendly='Nyheder', extra='Nyheder')
casters['audio'].addChannel(link='http://50.7.99.163:11067/256', friendly='80s',extra='Musik')
casters['audio'].addChannel(link= 'http://7599.live.streamtheworld.com:80/977_80AAC_SC', friendly='80s 977', extra='Musik')
casters['audio'].addChannel(link= 'http://7599.live.streamtheworld.com:80/977_90AAC_SC', friendly='90s 977', extra='Musik')


casters['video'].addChannel(link='http://dr01-lh.akamaihd.net/i/dr01_0@147054/master.m3u8', friendly='DR1', media='video/mp4')
casters['video'].addChannel(link='http://dr02-lh.akamaihd.net/i/dr02_0@147055/master.m3u8', friendly='DR2', media='video/mp4')
casters['video'].addChannel(link='http://dr03-lh.akamaihd.net/i/dr03_0@147056/master.m3u8', friendly='DR3', media='video/mp4')
casters['video'].addChannel(link='http://dr04-lh.akamaihd.net/i/dr04_0@147057/master.m3u8', friendly='DRK', media='video/mp4')
casters['video'].addChannel(link='http://dr05-lh.akamaihd.net/i/dr05_0@147058/master.m3u8', friendly='Ramasjang', media='video/mp4')
casters['video'].addChannel(link='http://dr06-lh.akamaihd.net/i/dr06_0@147059/master.m3u8', friendly='Ultra', media='video/mp4')

class medialist:
  def GET(self, device):
    od = collections.OrderedDict(sorted(casters[device].channels.items()))
    return json.dumps(od)
    
class list_players:
  def GET(self):
    return json.dumps(casters.keys());
    
class get_player:
  def GET(self, device):
    m = casters[device]
    return m.state_json()
     
class control_player:
  def GET(self, device, command):
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

class play_media:
  def GET(self, device, media):
    player = casters[device]
    player.play(media)
    time.sleep(1)
    return player.state_json()

class test:
  def GET(self):
    player = casters['video']
    return player.status

if __name__ == "__main__":
  app.run()
