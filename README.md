Chromecast to MQTT
==================

Python program to enable MQTT control endpoints for chromecasts (both audio and video). 

It listens to events from the connected chromecasts, and send their status to MQTT on the following events:
* Change in which app is running
* Media events (play, pause, stop etc.)
* Media information (title, artist, album etc)

It also listens to a MQTT topic, for commands. So you can send commands to your chromecasts like play, pause, stop etc.

Table of contents
===
<!--ts-->
   * [Chromecast to MQTT](#chromecast-to-mqtt)
   * [Table of contents](#table-of-contents)
   * [Installation](#installation)
      * [Starting python script with virtual-environment](#starting-python-script-with-virtual-environment)
      * [Starting with systemd](#starting-with-systemd)
      * [Start in a docker container](#start-in-a-docker-container)
      * [Command line options](#command-line-options)
   * [MQTT topics](#mqtt-topics)
      * [Topics reported on by chromecast2mqtt](#topics-reported-on-by-chromecast2mqtt)
      * [Controlling your chromecast via mqtt](#controlling-your-chromecast-via-mqtt)
      * [Send command to all registered chromecasts](#send-command-to-all-registered-chromecasts)
   * [Logging](#logging)
   * [Thanks to](#thanks-to)

<!-- Added by: thomas, at: lør  2 nov 13:25:18 CET 2019 -->

<!--te-->

Installation
===

Starting python script with virtual-environment
-----------------------------------------------

First ensure that you have at least python3.6 and venv installed, then create a new virtual environment for your python script:

```shell
$ python3 -m venv ~/chrome2mqtt
$ source ~/chrome2mqtt/bin/activate
cd ~/chrome2mqtt
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
ExecStart=/home/pi/chrome2mqtt/bin/python -m chrome2mqtt -max 2 

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
usage: chrome.py [-h] -max MAX [-p PORT] [-c CLIENT] [-r ROOT] [-m HOST]
                 [-l LOG] [-V]

Chromecast 2 mqtt

optional arguments:
  -h, --help            show this help message and exit
  -max MAX, --MAX MAX   Max number of chromecasts to expect
  -p PORT, --port PORT  MQTT port on host
  -c CLIENT, --client CLIENT
                        Client name for mqtt
  -r ROOT, --root ROOT  MQTT root topic
  -H HOST, --host HOST  MQTT Host
  -l LOGFILE, --logfile LOGFILE
                        Log to filename
  -d, --debug           loglevel debug
  -v, --verbose         loglevel info
  -V, --version         show program's version number and exit
  -C, --cleanup         Cleanup mqtt topic on exit
```

MQTT topics
===========

Topics reported on by chromecast2mqtt
-------------------------------------
Each chromecast will be configured with a separate mqtt topic, consisting of `<MQTT_ROOT>//friendly_name`, where friendly name, is a normalized version of the friendly name given to each chromecast, where the name is converted to lower cases, and spaces have been replaced with underscores.

The following topics will be used:

| Topic | Payload |
| ----- | ------- |
| <MQTT_ROOT>/<FRIENDLY_NAME>/app | Name of the currently running app (netflix, spotify, hbo, tidal etc). |
| <MQTT_ROOT>/<FRIENDLY_NAME>/state | Current state of the chromecast (playing, paused, buffering) |
| <MQTT_ROOT>/<FRIENDLY_NAME>/volume | Current volume level (an integer value between 0 and 100) |
| <MQTT_ROOT>/<FRIENDLY_NAME>/media | Returns a json object containing detailed information about the stream that is playing. Depending on the information from the app vendor. |
| <MQTT_ROOT>/<FRIENDLY_NAME>/capabilities | Json object containing the capabilities of the current activated app |

json formats for media and capabilities are as follows:

media object:
```javascript
{
  "title": string,
  "artist": string,
  "album": string,
  "album_art": string, // URL to a static image for the current playing track
  "metadata_type": number,
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
------------------------------------
It's possible to control the chromecasts, by sending a message to the `<MQTT_ROOT>/friendly_name/control/<action>` endpoint for each device, where `<action>` is one of the following list, some takes a payload as well:

| Action | Payload required | Value for payload |
| ------ | ------- | ----------------- |
| play | Optional | If no payload, just starts from a pause condition, otherwise send a json object {"link":string, "type": string} |
| pause | Optional | If no payload is supplied it will toggle pause state, otherwise send 1/True to pause or 0/False to play |
| stop | No | |
| next | No | |
| prev | No | |
| mute | Optional| If no payload is supplied it will toggle mute state, otherwise send 1/True to mute or 0/False to unmute |
| volume | Required|Integer 0 - 100 specifying volume level |

The json object for the play command contains a link to the media file you want to play, and a mime type for the content:

```javascript
// Start playing a mp3 audio file
 { "link": "https://link.to/awesome.mp3", "type": "audio/mp3" } 

// Start playing a mp4 video file
 { "link": "https://link.to/awesome.mp4", "type": "video/mp4" } 
 
// Special mimetype "youtube"
 { "link": "zSmOvYzSeaQ", "type": "youtube" }
```

if a command fails for some reason, a mqtt message will be posted to the debug topic `<MQTT_ROOT>/debug/commandresult`

Send command to all registered chromecasts
------------------------------------------
An extra listening endpoint is created on `<MQTT_ROOT>/control/<action>`, which will send the command (from table above) to all registered chromecast devices.

*Please note The above command layout breaks compability with earlier incarnations, where some commands where sent as payload to `<MQTT_ROOT>/friendly_name/control`, the old method is enabled as a fallback solution, to keep existing mqtt implementations working. The script will log a warning though, to let you know that you are using a deprecated method. It is strongly advicable to upgrade your mqtt setup to use the new endpoints*

Logging
=======
Logging can be configured in two ways, either simple with commandline options, -v for verbose (loglevel INFO and higher) or -d for debug (loglevel DEBUG or higher). You can also specify a file to dump your logs to with -l / --logfile.

A more advanced setup is to make a json file in your root project with the name logsetup.json, an example file (logsetup.json-example) is included, that you can rename and use as a basis for your own setup. This file will take precedence over the commandline arguments, which will be ignored if the file is found.

Thanks to
=========
I would like to thank [Paulus Schoutsen](https://github.com/balloob) for his excelent work on [pychromecast](https://github.com/balloob/pychromecast), without his library this project couldn't have been made.
