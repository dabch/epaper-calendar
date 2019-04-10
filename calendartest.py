#!/usr/bin/python3

from icalevents.icalevents import events
from dateutil.parser import parse
import datetime

url = ''

start = datetime.datetime.now()
end = start + datetime.timedelta(days=100)

evs = events(url, start=start, end=end)

evs.sort()
for e in evs:
    print(e)

