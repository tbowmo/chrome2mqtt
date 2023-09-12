FROM python:3.7.4-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
COPY requirements ./requirements
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY chrome2mqtt/ chrome2mqtt/
ENTRYPOINT [ "python", "-m", "chrome2mqtt" ]
