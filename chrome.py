#!/usr/bin/python3
import web
import pychromecast
import time
import json
import collections
from chromeevent import ChromeStatusUpdater
from streamdata import streamdata

urls = (
  '/', 'list_players',
  '/test', 'test',
  '/([a-z]*)', 'get_player',
  '/([a-z]*)/list', 'medialist',
  '/([a-z]*)/play/(.*)', 'play_media',
  '/([a-z]*)/([a-z]*)', 'control_player'
  )

app = web.application(urls, globals())

# Using IP address, rather than name, speeds up the startup of the program
audio = pychromecast.Chromecast('Chromecast-Audio') #get_chromecast(friendly_name="Chrome Audio Stuen")
audio.wait()

video = pychromecast.Chromecast('Chromecast') #get_chromecast(friendly_name="Chrome TV Stuen")
video.wait()


streams = streamdata()

streams.addChannel(link='http://live-icy.gss.dr.dk:80/A/A05H.mp3', friendly = 'DR P3', extra = 'Musik', xmlid = "p3.dr.dk")
streams.addChannel(link='http://live-icy.gss.dr.dk:80/A/A04H.mp3', friendly = 'DR P2', extra = 'Musik', xmlid = "p2.dr.dk")
streams.addChannel(link='http://live-icy.gss.dr.dk:80/A/A03H.mp3', friendly='DR P1', xmlid = "p1.dr.dk")
streams.addChannel(link='http://live-icy.gss.dr.dk:80/A/A10H.mp3', friendly='DR P4', xmlid = "p4.dr.dk")
streams.addChannel(link='http://live-icy.gss.dr.dk:80/A/A29H.mp3', friendly='DR P6', xmlid = "p6.dr.dk")
streams.addChannel(link='http://live-icy.gss.dr.dk:80/A/A21H.mp3', friendly='DR P7', xmlid = "p7.dr.dk")
streams.addChannel(link='http://live-icy.gss.dr.dk:80/A/A24H.mp3', friendly='Ramasjang', extra='børn')
streams.addChannel(link='http://live-icy.gss.dr.dk:80/A/A02H.mp3', friendly='Nyheder', extra='Nyheder', xmlid='nyheder.dr.dk')
streams.addChannel(link='http://50.7.99.163:11067/256', friendly='80s',extra='Musik')
streams.addChannel(link= 'http://7599.live.streamtheworld.com:80/977_80AAC_SC', friendly='80s 977', extra='Musik')
streams.addChannel(link= 'http://7599.live.streamtheworld.com:80/977_90AAC_SC', friendly='90s 977', extra='Musik')


streams.addChannel(link='http://dr01-lh.akamaihd.net/i/dr01_0@147054/master.m3u8', friendly='DR1', media='video/mp4', xmlid='dr1.dr.dk')
streams.addChannel(link='http://dr02-lh.akamaihd.net/i/dr02_0@147055/master.m3u8', friendly='DR2', media='video/mp4', xmlid='dr2.dr.dk')
streams.addChannel(link='http://dr03-lh.akamaihd.net/i/dr03_0@147056/master.m3u8', friendly='DR3', media='video/mp4', xmlid='dr3.dr.dk')
streams.addChannel(link='http://dr04-lh.akamaihd.net/i/dr04_0@147057/master.m3u8', friendly='DRK', media='video/mp4', xmlid='k.dr.dk')
streams.addChannel(link='http://dr05-lh.akamaihd.net/i/dr05_0@147058/master.m3u8', friendly='Ramasjang', media='video/mp4', xmlid='ramasjang.dr.dk')
streams.addChannel(link='http://dr06-lh.akamaihd.net/i/dr06_0@147059/master.m3u8', friendly='Ultra', media='video/mp4', xmlid='ultra.dr.dk')

casters = {
  'video' : ChromeStatusUpdater(video,156, streams),
  'audio' : ChromeStatusUpdater(audio,157, streams)
  }  


class medialist:
  def GET(self, device):
    #od = collections.OrderedDict(sorted(casters[device].getChannelList().items()))
    od = casters[device].getChannelList()
    return json.dumps(od)
    
class list_players:
  def GET(self):
    return json.dumps(list(casters.keys()));
    
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
