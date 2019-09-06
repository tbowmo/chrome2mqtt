#!/usr/bin/python3
"""
    Program that handles chromecast integration to mqtt. 

    Copyright 2018: Thomas Bowman Morch
"""
import pychromecast
from globalmqtt import GlobalMQTT
from chromeevent import ChromeEvent
from os import environ
from mqtt import MQTT
from time import sleep, strftime
from datetime import datetime
import sys
import logging
import socket
import atexit
import signal

__version__ = __VERSION__ = "1.0.0"

mqtt_client = socket.gethostname()

def parse_args(argv = None):
    import argparse
    parser = argparse.ArgumentParser(description='Chromecast 2 mqtt')
    required_flags = parser.add_mutually_exclusive_group(required=True)
    required_flags.add_argument('-max', '--MAX', action="store",type=int, default=None, help="Max number of chromecasts to expect")
    parser.add_argument('-p', '--port', action="store", default=1883, type=int, help="MQTT port on host")
    parser.add_argument('-c', '--client', action="store", default=socket.gethostname(), help="Client name for mqtt")
    parser.add_argument('-r', '--root', action="store", default="chromecast", help="MQTT root topic")
    parser.add_argument('-H', '--host', action="store", default="127.0.0.1", help="MQTT Host")
    parser.add_argument('-l', '--logfile', action="store", default=None, help="Log to filename")
    parser.add_argument('-d', '--debug', action="store_const", dest="log", const=logging.DEBUG, help="loglevel debug")
    parser.add_argument('-v', '--verbose', action="store_const", dest="log", const=logging.INFO, help="loglevel info")
    parser.add_argument('-V', '--version', action='version', version='%(prog)s {version}'.format(version=__VERSION__))

    return parser.parse_args(argv)

def start_banner(args):
    print('Chromecast2MQTT by tbowmo')
    print('Connecting to mqtt host ' + args.host + ' port ' + str(args.port))
    print('Using mqtt root ' + args.root)

def mqtt_init(mqtt_port, mqtt_host, mqtt_root):
    """Initialize mqtt transport"""
    try:
        mqtt_port = int(mqtt_port)
        mqtt = MQTT(host=mqtt_host, port=mqtt_port, client=mqtt_client)
        mqtt.conn()
        mqtt.loop_start()
        mqtt.publish(mqtt_root + '/debug/start', datetime.now().strftime('%c'), retain=True)
        return mqtt
    except:
        print('Error connecting to mqtt host ' + mqtt_host + ' on port ' + str(mqtt_port))
        sys.exit(1)

def main_loop():
    """Main operating loop, discovers chromecasts, and run forever until ctrl-c is received"""
    casters = {}
    def callback(chromecast):
        chromecast.connect()
        nonlocal casters
        name = chromecast.device.friendly_name
        print('Found :', name)
        casters.update({name: ChromeEvent(chromecast, mqtt, args.root)})

    stop_discovery = pychromecast.get_chromecasts(callback=callback, blocking=False)
    def signal_handler(sig, frame):
        print('Shutting down')
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        if (args.MAX>0 and len(casters) == args.MAX):
            stop_discovery()
            signal.pause()
            GlobalMQTT(casters, mqtt, args.root)
        sleep(1)

def lastWill():
    """Send a last will to the mqtt server"""
    mqtt.publish(args.root + '/debug/stop', datetime.now().strftime('%c'), retain=True)


args = parse_args()
start_banner(args)

if (args.logfile != None):
    logging.basicConfig(level=args.log,
                        filename=args.file,
                        format = '%(asctime)s %(levelname)-8s %(message)s')
else:
    logging.basicConfig(level=args.log,
                        format = '%(asctime)s %(levelname)-8s %(message)s')
    

if args.MAX == 0:
    print('WARNING! max casters is set to 0, which means the script will never stop listening for new casters')
    print('specify --max= to set the maximum number of chromecasts to expect')

mqtt = mqtt_init(args.port, args.host, args.root)
atexit.register(lastWill)

if __name__ == '__main__':
    main_loop()
