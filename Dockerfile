FROM python:3
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV MQTT_HOST=jarvis
ENV MQTT_PORT=1883
ENV MQTT_ROOT=chromecast

CMD [ "python", "./chrome.py" ]

EXPOSE 8181/TCP

VOLUME /config
