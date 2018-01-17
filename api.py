from bottle import request, response
from bottle import get
import time
import json

casters = {}

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
    print(media)
    player = casters[device]
    player.play(media)
    time.sleep(1)
    return player.state_json()

@get('/status')
def status():
    player = casters['video']
    if player.status.chromeApp != "Backdrop" and player.status.chromeApp != "":
        return player.state_json();
    else:
        player = casters['audio']
        return player.state_json();

