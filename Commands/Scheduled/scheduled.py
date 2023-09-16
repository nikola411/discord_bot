from datetime import datetime, timedelta, time
import re

ACTIONS = ['msg', 'img']
TIMESTAMP = 'vreme'
CONTENT = 'sadrzaj'
TYPE = 'tip'

TYPE_RE = r'(tip)\=\[(msg|img)\]'
CONTENT_RE = r'(sadrzaj)\=\[([^\]]+)\]'
TIMESTAMP_RE = r'(vreme)\=\[([^\]]+)\]'
TIME_RE = r'([0-9]{1,2})\:([0-9]{1,2})\:([0-9]{1,2})'
DATE_RE = r'([0-9]{1,2})\.([0-9]{1,2})\.([0-9]{4})'

FIELDS = [TYPE_RE, CONTENT_RE, TIMESTAMP_RE]

class Schedule:
    scheduled = []

    def AddScheduledEvent(self, words: list) -> bool:
        input = ' '.join(words)
        entry = {}

        for reg in FIELDS:
            capture = re.search(reg, input)
            if capture is None:
                return False
            capture = capture.groups()
            entry[capture[0]] = capture[1]
        
        date_capture = re.search(DATE_RE, entry[TIMESTAMP])
        time_capture = re.search(TIME_RE, entry[TIMESTAMP])

        if date_capture is None and time_capture is None:
            return False
        
        now = datetime.now()
        date = (now.year, now.month, now.day) if date_capture is None else date_capture.groups()
        time = (now.hour, now.minute, now.second) if time_capture is None else time_capture.groups()
               
        entry[TIMESTAMP] = datetime(int(date[2]), int(date[1]), int(date[0]), int(time[0]), int(time[1]), int(time[2]))
        self.scheduled.append(entry)
        return True

    def GetExpired(self) -> list:
        expired = [event for event in self.scheduled if (event[TIMESTAMP] - datetime.now()).total_seconds() <= 0]
        self.scheduled = [event for event in self.scheduled if event not in expired]
        return expired

