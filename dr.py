import xml.etree.ElementTree as ET
from datetime import datetime
from datetime import timedelta
from pytz import timezone

class Dr:
    def __init__(self, content_id):
        self.program = None
        tz = timezone('Europe/Copenhagen')
        now = datetime.now(tz)
        self.nextStart = now + timedelta(seconds=600)
        try:
            tree = ET.parse('/config/xmltv/'+content_id + '.xml')
            root = tree.getroot()
            for prg in root.findall('programme'):
                if prg.get('channel') == content_id:
                    start = datetime.strptime(prg.get('start'),"%Y%m%d%H%M%S %z")
                    stop = datetime.strptime(prg.get('stop'),"%Y%m%d%H%M%S %z")
                    if start < now and stop > now:
                        self.program = prg
                    if start > datetime.now(tz):
                        self.nextStart = start
                        return
        except:
            pass

    def title(self):
        if self.program is None:
            return "Intet program"
        return self.program.find('title').text
    
    def start(self):
        if self.program is None:
            return (datetime.now()).isoformat()
        return datetime.strptime(self.program.get('start'),"%Y%m%d%H%M%S %z").isoformat()

    def stop(self):
        if self.program is None:
            return (self.nextStart).isoformat()
        return datetime.strptime(self.program.get('stop'),"%Y%m%d%H%M%S %z").isoformat()