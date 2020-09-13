Chrome2MQTT
==================

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=tbowmo_chrome2mqtt&metric=alert_status)](https://sonarcloud.io/dashboard?id=tbowmo_chrome2mqtt)

Python program to enable MQTT control endpoints for chromecasts (both audio and video).

It listens to events from the connected chromecasts, and send their status to MQTT on the following events:
* Change in which app is running
* Media events (play, pause, stop etc.)
* Media information (title, artist, album etc)

It also listens to a MQTT topic, for commands. So you can send commands to your chromecasts like play, pause, stop etc.

**NOTE!** Chromecast devices are collected into rooms, old operation where devices are treated seperately is available with option ```--standalone```

Table of contents
===
<!--ts-->
   * [Chrome2MQTT](#chrome2mqtt)
   * [Table of contents](#table-of-contents)
   * [Installation](#installation)
      * [Starting python script with virtual-environment](#starting-python-script-with-virtual-environment)
      * [Starting with systemd](#starting-with-systemd)
      * [Start in a docker container](#start-in-a-docker-container)
      * [Command line options](#command-line-options)
   * [MQTT topics](#mqtt-topics)
      * [Rooms or single devices](#rooms-or-single-devices)
      * [Topics reported on by chromecast2mqtt](#topics-reported-on-by-chromecast2mqtt)
      * [Aliasing device topics](#aliasing-device-topics)
   * [JSON types](#json-types)
   * [Controlling your chromecast via mqtt](#controlling-your-chromecast-via-mqtt)
   * [Logging](#logging)
   * [Thanks to](#thanks-to)

<!-- Added by: thomas, at: søn 12 apr 22:29:18 CEST 2020 -->

<!--te-->

Installation
===

Starting python script with virtual-environment
-----------------------------------------------

First ensure that you have at least python3.6 and venv installed, then create a new virtual environment for your python script:

```shell
$ git clone https://github.com/tbowmo/chrome2mqtt.git
$ cd chrome2mqtt
$ python3 -m venv .
$ source ./bin/activate
$ pip install --no-cache-dir -r requirements.txt
```

You are now ready to start the script with

`python -m chrome2mqtt <options>`

Starting with systemd
---
Start by following the description for enabling a virtual environment for python

Then create a file named .service in /etc/systemd/system, with the following content (update paths and hosts as desired)
```
[Unit]
Description=Chrome2mqtt
Wants=network.target
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/pi/chrome2mqtt
ExecStart=/home/pi/chrome2mqtt/bin/python -m chrome2mqtt

[Install]
WantedBy=multi-user.target
```

Then in a terminal, execute the following two commands to enable your new service
```shell
# systemctl enable chrome2mqtt.service
# systemctl start chrome2mqtt.service
```

Start in a docker container
---
If you wish to run inside a docker container, you can build your own image with `docker build . --tag chrome2mqtt` and then run it with `docker run chrome2mqtt <options>` 

Command line options
-------------
Configure through command line options, as shown below
```
usage: chrome2mqtt [-h] [--mqttport MQTTPORT] [--mqttclient MQTTCLIENT] [--mqttroot MQTTROOT] [--mqttuser MQTTUSER] [--mqttpass MQTTPASS] [-H MQTTHOST] [-l LOGFILE] [-d] [-v] [-V] [-C] [-S] [--alias ALIAS]

chrome2mqtt

Connects your chromecasts to a mqtt-broker

optional arguments:
  -h, --help            show this help message and exit
  --mqttport MQTTPORT   MQTT port on host
  --mqttclient MQTTCLIENT
                        Client name for mqtt
  --mqttroot MQTTROOT   MQTT root topic
  --mqttuser MQTTUSER   MQTT user (if authentication is enabled for the broker)
  --mqttpass MQTTPASS   MQTT password (if authentication is enabled for the broker)
  -H MQTTHOST, --mqtthost MQTTHOST
                        MQTT Host
  -l LOGFILE, --logfile LOGFILE
                        Log to filename
  -d, --debug           loglevel debug
  -v, --verbose         loglevel info
  -V, --version         show program's version number and exit
  -C, --cleanup         Cleanup mqtt topic on exit
  -S, --standalone      Split into separate devices
  --alias ALIAS         topic aliases for devices

See more on https://github.com/tbowmo/chrome2mqtt/README.md
```

MQTT topics
===========

Rooms or single devices
-----------------------
chrome2mqtt can organize devices into rooms, or as standalone devices. Normal operation is to organize into rooms, where it can collect two devices (one audio and one video) into one endpoint, automatically directing commands to the active device.

If you send a play command with an audio stream to a room, then it will automatically send this to the audio chromecast, and if you send a video stream it will be sent to the video chromecast. When starting the a new stream on an inactive chromecast, the other device will automatically be stopped, if it is playing.

In rooms mode, it will use the device name of your chromecast to identify which room it is placed in. To do this you must have the follow the following scheme for naming the devices `\<room>_tv` or `\<room>_audio`. As an example, my chromecasts are named `livingroom_tv`and `livingroom_audio`, then I get a topic called `<MQTT_ROOT>/livingroom/...`

In standalone mode each device is treated as a separate one, and will have separate topics in your mqtt tree, the topic name will be a a normalized version of the friendly name given to each chromecast, where the name is converted to lower cases, and spaces have been replaced with underscores.

Topics reported on by chromecast2mqtt
-------------------------------------
Each room (or device if using `--standalone` will have a set of mqtt topics where status will be emitted
The following topics will be used:

| Topic | Payload |
| ----- | ------- |
| <MQTT_ROOT>/\<ROOM>/app | Name of the currently running app (netflix, spotify, hbo, tidal etc). |
| <MQTT_ROOT>/\<ROOM>/state | Current state of the chromecast (playing, paused, buffering) |
| <MQTT_ROOT>/\<ROOM>/volume | Current volume level (an integer value between 0 and 100) |
| <MQTT_ROOT>/\<ROOM>/media | Returns a json object containing detailed information about the stream that is playing. Depending on the information from the app vendor. |
| <MQTT_ROOT>/\<ROOM>/capabilities | Json object containing the capabilities of the current activated app |

*Notes:*  
*MQTT_ROOT is specified through option `--mqttroot` and will default to empty if not specified.*  
*ROOM will be device, if `--standalone` is specified*

Aliasing device topics
----------------------
By supplying the `--alias` option and a list of device / alias pairs, you can rename your device topics. Specify a comma separated list of device / topic alias pairs:
`device1=alias/path1,device2=alias/path2` if an alias is not found for a device upon discovery, then the device name itself will be used in topic generation.

*NOTE* When running with `--standalone` you need to specify the full devicename, in lowercases and spaces converted into "_", that is if you have a device named "Livingroom audio" then you need to specify "livingroom\_audio" as device name. If running in standard mode (where chromecasts are collected into rooms), you need to use the room name for the device in aliasing.

All aliases will have mqtt_root topic prepended (specified through option `--mqttroot`)

JSON types
==========
json formats for media and capabilities are as follows:

media object:
```javascript
{
  "title": string,
  "artist": string,
  "album": string,
  "album_art": string, // URL to a static image for the current playing track
  "metadata_type": number,
  "duration": number, // Total duration of the current media track
  "current_time": number, // current time index for the playing media
  "last_update": number, // timestamp for last media update
}
```

capabilities object, this is a json containing state and feature capabilities of the current stream playing:
```javascript
{
  "state": string, // same as sent to <mqtt_root>/<friendly_name>/state
  "volume": integer, // same as sent to <mqtt_root>/<friendly_name>/volume
  "muted": boolean,    // indicates if device is muted
  "app": string, // same as sent to <mqtt_root>/<friendly_name>/app
  "app_icon": string, // url to a icon / image representing the current running app (Netflix, spotify etc. logo)
  "supported_features": {
    "skip_fwd": boolean, // indicates if skip_fwd is available
    "skip_bck": boolean, // indicates if skip_bck is available
    "pause": boolean,    // indicates if pause is available
    "volume": boolean,   // indicates if volume control is available
    "mute": boolean,     // indicates if audio stream can be muted
  }
}
```

Controlling your chromecast via mqtt
====================================
It's possible to control the chromecasts, by sending a message to the `<MQTT_ROOT>/\<ROOM>/control/<action>` endpoint for each device, where `<action>` is one of the following list, some takes a payload as well:

| Action | Payload required | Value for payload |
| ------ | ------- | ----------------- |
| play | Optional | If no payload, just starts from a pause condition, otherwise send a json object {"link":string, "type": string} |
| pause | Optional | If no payload is supplied it will toggle pause state, otherwise send 1/True to pause or 0/False to play |
| stop | No | |
| next | No | |
| prev | No | |
| mute | Optional| If no payload is supplied it will toggle mute state, otherwise send 1/True to mute or 0/False to unmute |
| volume | Required|Integer 0 - 100 specifying volume level |
| update | No | Requests the chromecast to send a media status update
| quit | No | Quit the currently running app on the chromecast

Play
----
The json object for the play command contains a link to the media file you want to play, and a mime type for the content:

```javascript
// Start playing a mp3 audio file
 { "link": "https://link.to/awesome.mp3", "type": "audio/mp3" }

// Start playing a mp4 video file
 { "link": "https://link.to/awesome.mp4", "type": "video/mp4" } 
 
// Special mimetype "youtube"
 { "link": "zSmOvYzSeaQ", "type": "youtube" }
```

Logging
=======
Logging can be configured in two ways, either simple with commandline options, -v for verbose (loglevel INFO and higher) or -d for debug (loglevel DEBUG or higher). You can also specify a file to dump your logs to with -l / --logfile.

A more advanced setup is to make a json file in your root project with the name logsetup.json, an example file (logsetup.json-example) is included, that you can rename and use as a basis for your own setup. This file will take precedence over the commandline arguments, which will be ignored if the file is found.

Thanks to
=========
I would like to thank [Paulus Schoutsen](https://github.com/balloob) for his excelent work on [pychromecast](https://github.com/balloob/pychromecast), without his library this project couldn't have been made.
