# Chromecast to MQTT

## Features

Small python program, to enable MQTT control endpoints for chromecasts. 

It listens to events from the connected chromecasts, and send their status to MQTT, on the following events:
* Change in which app is running
* Media events (play, pause, stop etc.)
* Media information (title, artist, album etc)

It also listens to a MQTT topic, for commands. So you can send commands to your chromecasts, like play, pause, stop etc.

## Configuration
The script is configured either through environment variables, or commandline options, which defaults to the shown values below:

| env variable | cmd line option | default values
|---|---|---|
| MQTT_HOST | --host | 127.0.0.1
| MQTT_PORT | --port | 1883
| MQTT_ROOT | --root | chromecast
|           | --log  | 20

Commandline options takes precedense over environment variables.

# MQTT topics
## topics sent to by chromecast2mqtt
Each chromecast will be configured with a separate mqtt topic, consisting of `<MQTT_ROOT>//friendly_name`, where friendly name, is a normalized version of the friendly name given to each chromecast, where the name is converted to lower cases, and spaces have been replaced with underscores.

The following topics will be used:
* <MQTT_ROOT>/<FRIENDLY_NAME>/app
  * will be used for the currently running app (netflix, spotify, hbo, tidal etc).
* <MQTT_ROOT>/<FRIENDLY_NAME>/state
  * will be used for the current activity state (playing, paused, buffering)
* <MQTT_ROOT>/<FRIENDLY_NAME>/media
  * will contain detailed information about the stream that is playing. Depending on the information from the app vendor.

## Control endpoints listened on
It's possible to control the chromecasts, by sending a message to the `<MQTT_ROOT/friendly_name/control` endpoint for each device, send a payload with one of the following commands: play, pause, stop, fwd, rew, quit.

if you want to start playing a new media, then you can use the endpoint `<root topic>/cast/control/play`, send the URL for your media as payload

a simple global mqtt topic is also present, at `<MQTT_ROOT>/control`, this accepts the following commands: pause, play, stop, quit. The command will be sent to all registered chromecasts. This makes it possible to pause ALL chromecasts with one command.

# Docker
the included Dockerfile can be used to build a docker image, with the following command

```
docker build -t chromecast-integrator .
```

afterwards start it with 

```
docker run --name chromecast --restart unless-stopped -v /opt/chromecast:/config -d -t --net=host chromecast-integrator
```
