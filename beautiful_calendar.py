#!/usr/bin/python3
import datetime
import math
import sys

import epd7in5
from PIL import Image, ImageDraw, ImageFont

import ical_worker
from config import *

#timezone = pytz.timezone(TIMEZONE)
#ical_worker.basetime = datetime.datetime.now(timezone)
#ical_worker.basetime.astimezone(timezone)

fheadline = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Light.ttf', headline_size)
ftext = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Light.ttf', text_size)
fbold = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', text_size)
#fawesome = ImageFont.truetype('fa-regular.otf', text_size)

print("DAYS: {}".format(DAYS))
print("hours_day: {}".format(hours_day))
def get_drawable_events():
    print("per_hour: {}\t lost: {}".format(per_hour, height - bar_top - offset_top - offset_allday - hours_day * per_hour))
print("per_day: {}\t lost: {}".format(per_day, width - bar_left - offset_left - per_day * DAYS))
epd = epd7in5.EPD()

def prepare_grid(d):
    """ Prepares the Days X Hours grid for drawing events into it """

    # separate top bar from rest
    d.line([(offset_left, offset_top + bar_top - 1), (width, offset_top + bar_top - 1)], width=2)
    # separate all-day events from grid
    d.line([(offset_left, offset_top + bar_top + offset_allday), (width, offset_top + bar_top + offset_allday)], width=2)
    # separate the left bar from the rest
    d.line([(offset_left + bar_left -1, offset_top), (offset_left + bar_left - 1, height)], width=2)


    # draw the vertical day separators and day headlines
    for i in range(0, DAYS):
        x = offset_left + bar_left + per_day * i
        # for every but the first, draw separator to the left
        if i > 0: 
            d.line([(x, offset_top), (x, height)])
        # draw date headline
        day = ical_worker.basetime + datetime.timedelta(days=i)
        headline = day.strftime('%a, %d')
        textsize_x = d.textsize(headline, fheadline)[0]
        textoffs_x = math.floor((per_day - textsize_x) / 2)
        d.text((x + textoffs_x, offset_top), headline, font=fheadline) 
    
    # draw horizontal hour separators and hour numbers
    for i in range(0, hours_day):
        y = offset_top + bar_top + offset_allday + per_hour * i
        # for every but the first, draw separator before
        if i > 0:
            # separator = dotted line with every fourth pixel
            for j in range(offset_left, width, 4):
                d.point([(j, y)])
        # draw the hour number
        textoffs_y = math.floor((per_hour - text_size) / 2)
        d.text((offset_left, y + textoffs_y - 1), "%02d" % (BEGIN_DAY + i), font=fheadline)

    # clear the all-day events space
    d.rectangle((offset_left + bar_left + 1, offset_top + bar_left + 1, width, offset_top + bar_left + offset_allday - 1), fill=200, width=0)

def draw_short_event(d, e):
    """
    Internal function for drawing events into the grid.
    
    Not to be used for drawing events manually, please use draw_event for that.
    
    This function cannot draw events lasting across midnight. Instead, such events are split up
    into several calls of draw_short_event and draw_allday_event.
    
    """
    x_start = offset_left + bar_left + e["day"] * per_day + e["column"] * per_day / e["max_collision"]
    y_start = offset_top + bar_top + offset_allday + math.floor((e["start"] - (BEGIN_DAY * 60)) * per_hour / 60)
    width = per_day / e["max_collision"]
    y_end = offset_top + bar_top + offset_allday + math.floor((e["end"] - (BEGIN_DAY * 60)) * per_hour / 60)
    # clear the event's area and make the outline
    d.rectangle((x_start, y_start, x_start + width, y_end), outline=0, width=2, fill=200)

    textoffs_x = 5
    textoffs_y = (per_hour - text_size) // 2 - 1
    
    fulltext = e["title"]
    while d.textsize(fulltext, font=ftext)[0] > width - 2 * textoffs_x and len(fulltext) > 0:
        fulltext = fulltext[:-1]
    if e["end"] - e["start"] >= 90:
        begintext = "%02d:%02d" % (e["start"] // 60, e["start"] % 60)
        endtext = "%02d:%02d" % (e["end"] // 60, e["end"] % 60)
        datetext = "\n%s-%s" % (begintext, endtext)
        if d.textsize(datetext, font=ftext)[0] > width - 2 * textoffs_x:
           datetext = "\n%s" % begintext
        if d.textsize(datetext, font=ftext)[0] <= width - 2 * textoffs_x:
            fulltext += datetext
    d.text((x_start + textoffs_x, y_start + textoffs_y), fulltext, font=ftext) 
    print(fulltext)
    #d.text((x_start + 5, y_start + text_size + textoffs_y), begintext + "-" + endtext, font=ftext) 
    
    print(e)

def draw_allday_event(d, ev):
    """ 
    Internal function for drawing events that shouldn't appear in the grid.
    
    Not to be used for drawing events manually, please use draw_event for that.
    """
    if e["column"] >= ALLDAY_MAX:
        return
    x_start = offset_left + bar_left + e["start"] * per_day - 1
    x_end = offset_left + bar_left + e["end"] * per_day
    y_start = offset_top + bar_top + e["column"] * allday_size - 1
    width = x_end - x_start
    
    d.rectangle((x_start, y_start, x_end, y_start + allday_size + 2), outline=0, fill=200, width=2)

    textoffs_x = 5
    textoffs_y = (allday_size - text_size) // 2
    fulltext = e["title"]
    while d.textsize(fulltext, font=ftext)[0] > width - 2 * textoffs_x and len(fulltext) > 0:
        fulltext = fulltext[:-1]
    d.text((x_start + textoffs_x, y_start + textoffs_y), fulltext, font=ftext)
    
def draw_event(d, ev):
    """
    High-level function for drawing an event as it is generated by the iCal Library 

    d -- the Pillow.ImageDraw Object to draw onto
    ev -- the icalendar event Object to draw
    """
    pass

if __name__ == "__main__":
    (drawables, all_days) = ical_worker.get_drawable_events()
    im = Image.new('1', (width, height), 255)
    d = ImageDraw.Draw(im)

    prepare_grid(d)
    #draw_event(d, evs[1]) 
    for l in drawables:
        for e in l:
            draw_short_event(d, e)
    for e in all_days:
        draw_allday_event(d, e)
    im.save(open("out.jpg", "w+"))


    epd.init() 
    epd.display(epd.getbuffer(im))
    epd.sleep()
