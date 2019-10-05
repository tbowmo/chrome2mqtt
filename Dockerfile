FROM python:3
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY chrome2mqtt/ chrome2mqtt/
ENTRYPOINT [ "python", "-m", "chrome2mqtt" ]
