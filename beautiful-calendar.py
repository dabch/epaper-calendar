#!/usr/bin/python3

from icalevents.icalevents import events
#from dateutil.parser import parse
import datetime
import pytz # timezone
import configparser

import math
import sys

import epd7in5
from PIL import Image, ImageDraw, ImageFont

BEGIN_DAY = 8
END_DAY = 24
DAYS = 5
TIMEZONE = 'Europe/Berlin'

width = epd7in5.EPD_WIDTH 
height = epd7in5.EPD_HEIGHT
timezone = pytz.timezone(TIMEZONE)
basetime = datetime.datetime.now(timezone)
basetime.astimezone(timezone)

offset_top = 0 
offset_left = 0
bar_top = 42
bar_left = 20
hours_day = END_DAY - BEGIN_DAY
per_hour = math.floor((height - bar_top - offset_top) / hours_day)
per_day = math.floor((width - bar_left - offset_left) / DAYS)

text_size = 15

ftext = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Light.ttf', text_size)
fawesome = ImageFont.truetype('fa-regular.otf', text_size)


print("DAYS: {}".format(DAYS))
print("hours_day: {}".format(hours_day))
print("per_hour: {}\t lost: {}".format(per_hour, height - bar_top - offset_top - hours_day * per_hour))
print("per_day: {}\t lost: {}".format(per_day, width - bar_left - offset_left - per_day * DAYS))
epd = epd7in5.EPD()



conf = configparser.ConfigParser()
conf.read("config.ini")

url = conf['DEFAULT']['URL']


start = basetime.replace(hour=BEGIN_DAY,minute=0)
end = start + datetime.timedelta(days=DAYS)
#
evs = events(url, start=start, end=end)
#
evs.sort()
#


def prepare_grid(d):
    """ Prepares the Days X Hours grid for drawing events into it """

    # separate top bar from rest
    d.line([(offset_left, offset_top + bar_top - 1), (width, offset_top + bar_top - 1)], width=2)
    # separate the left bar from the rest
    d.line([(offset_left + bar_left -1, offset_top), (offset_left + bar_left - 1, height)], width=2)

    # draw the vertical day separators and day headlines
    for i in range(0, DAYS):
        x = offset_left + bar_left + per_day * i
        # for every but the first, draw separator to the left
        if i > 0: 
            d.line([(x, offset_top), (x, height)])
        # draw date headline
        day = basetime + datetime.timedelta(days=i)
        headline = day.strftime('%a, %d')
        textsize_x = d.textsize(headline, ftext)[0]
        textoffs_x = math.floor((per_day - textsize_x) / 2)
        d.text((x + textoffs_x, offset_top), headline, font=ftext) 
    
    # draw horizontal hour separators and hour numbers
    for i in range(0, hours_day):
        y = offset_top + bar_top + per_hour * i
        # for every but the first, draw separator before
        if i > 0:
            # separator = dotted line with every fourth pixel
            for j in range(offset_left, width, 4):
                d.point([(j, y)])
        # draw the hour number
        textoffs_y = math.floor((per_hour - text_size) / 2)
        d.text((offset_left, y + textoffs_y - 1), "%02d" % (BEGIN_DAY + i), font=ftext)

def draw_short_event(d, e):
    """
    Internal function for drawing events into the grid.
    
    Not to be used for drawing events manually, please use draw_event for that.
    
    This function cannot draw events lasting across midnight. Instead, such events are split up
    into several calls of draw_short_event and draw_allday_event by draw_event. 
    
    """
    x_start = offset_left + bar_left + e["day"] * per_day + 1
    y_start = offset_top + bar_top + math.floor((e["start"] - (BEGIN_DAY * 60)) * per_hour / 60)
    x_end = x_start + per_day - 2 # TODO collision management
    y_end = offset_top + bar_top + math.floor((e["end"] - (BEGIN_DAY * 60)) * per_hour / 60)
    d.rectangle((x_start, y_start, x_end, y_end), outline=0, fill=200)
    
    print(e)

def draw_allday_event():
    """ 
    Internal function for drawing events that shouldn't appear in the grid.
    
    Not to be used for drawing events manually, please use draw_event for that.
    """
    pass

    
def draw_event(d, ev):
    """
    High-level function for drawing an event as it is generated by the iCal Library 

    d -- the Pillow.ImageDraw Object to draw onto
    ev -- the icalendar event Object to draw
    """
    pass

def detect_collisions(drawables):
    """ Takes a list of drawable events (generated by split_events) and checks them 
    for collisions, i.e. events that need to be drawn side by side. Returns the same
    list of events with two parameters added to each event: index to be drawn in and
    number of events at that point. """ 
    
    collisions = [[[] for x in range(len(drawables))] for y in range(len(drawables))]
    for e in drawables:
        pass

def split_events(evs):
    drawables = [[] for x in range(DAYS)]
    all_days = []
    for ev in evs:
        start = ev.start.astimezone(timezone)
        end = ev.end.astimezone(timezone)
        if ev.all_day:
            # TODO draw_allday_event(d, ev)
            pass
        else:
            """ We will be drawing events that last across more than one day separately for
            each day. 
            
            variable explanations: (this shit is complicated...)

            days_duration: the number of days the event spans. For an event going from midnight
                        to midnight, this would be 1. For an event going from 23:55 to 00:05 this
                        would be 2.
                        This reflects the actual properties of the event and NOT the number
                        of days inside the calendar timeframe.
            
            start_day:  The index of the day on which the event starts, relative to our calendar
                        timeframe. 0 is the first day shown on the calendar, 1 the second etc.
                        start_day can be negative if the event has already started outside the
                        calendar timeframe (e.g. two days ago, then it would be -2)

            These two variables are then used to iterate over the intersection of the days that
            the event spans and the days inside the calendar timeframe, with the loop counter
            (named days) again being the current day's index relative to the calendar timeframe,
            just as start_day.
            So essentially we are iterating over range(start_day, start_day + days_duration), but
            because calendars are a bitch it's more complicated. The min and max just make sure 
            we only iterate over the days of the event that are in our calendar timeframe.
            """
            days_duration = (end.date() - start.date() + datetime.timedelta(days=1)).days
            start_day = (start.date() - basetime.date()).days # the start day index on our calendar (starting at 0 for today)
            #if start.date() < basetime.date(): # i.e. if event has started already
                #days_duration = (end.date() - basetime.date() + datetime.timedelta(days=1)).days
                #start_day = 0
            print("days_duration: {}\nstart_day: {}".format(days_duration, start_day))
            # correct for events that end at midnight the next day
            if end.hour == 0 and end == 0:
                days_duration -= 1
            for day in range(max(0, start_day), min(start_day + days_duration, DAYS)):
                event = {}
                if day == start_day: # first iteration - real start time
                    if start.hour >= END_DAY:
                        continue
                    elif start.hour < BEGIN_DAY:
                        event["start"] = BEGIN_DAY * 60 
                    else:
                        event["start"] = start.hour * 60 + start.minute
                else: # any later iteration - event going on from midnight
                    event["start"] = BEGIN_DAY * 60

                if day == start_day + days_duration - 1: # last iteration - real end time
                    if end.hour < BEGIN_DAY:
                        continue
                    elif end.hour >= END_DAY:
                        event["end"] = END_DAY * 60
                    else:
                        event["end"] = end.hour * 60 + end.minute
                else: # any earlier iteration - event going until end of day
                    event["end"] = END_DAY * 60
                event["title"] = ev.summary
                event["day"] = day
                # check duration to prevent event from being too small
                minutes_duration = event["end"] - event["start"]
                if minutes_duration < 60:
                    if event["end"] + 60 - minutes_duration >= END_DAY * 60:
                        event["end"] = END_DAY * 60
                        event["start"] = END_DAY * 60 - 60 
                    else:
                        event["end"] += 60 - minutes_duration
                #draw_short_event(d, event)
                drawables[day].append(event)
    return (drawables, all_days)  


if __name__ == "__main__":
    im = Image.new('1', (width, height), 255)
    d = ImageDraw.Draw(im)

    prepare_grid(d)
    #draw_event(d, evs[1]) 
    drawables, all_days = split_events(evs)
    for l in drawables:
        for e in l:
            draw_short_event(d, e)
    im.save(open("out.jpg", "w+"))


    epd.init() 
    epd.display(epd.getbuffer(im))
    epd.sleep()


    #logostr = ''
    #evstr = ''
    #for e in evs:
    #    title = e.summary
    #    #begin = e.start
    #    #end = e.end
    #    left = e.time_left()
    #    if left.total_seconds() > 0: # event in future
    #        if left.days > 0:
    #            leftstr = "{} days".format(left.days)
    #        else if left.seconds <= 3600: # more than one hour in future
    #            leftstr = "next hour"
    #        else:
    #            hours = left.seconds / 3600
    #            leftstr = "{} hours".format(hours)
    #    else: # event has started
    #        to_end = 
    #print(evstr)
    #d.text((0,  0), logostr, font=fawesome)
    #d.text((20, 0), evstr, font=f)
    

