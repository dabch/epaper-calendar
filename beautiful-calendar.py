#!/usr/bin/python3

from icalevents.icalevents import events
from dateutil.parser import parse
import datetime
import configparser

import math
import sys

import epd7in5
from PIL import Image, ImageDraw, ImageFont

BEGIN_DAY = 8
END_DAY = 24
DAYS = 4


if __name__ == "__main__":
    width = epd7in5.EPD_WIDTH
    height = epd7in5.EPD_HEIGHT

    offset_top = 0 
    offset_left = 0
    bar_top = 20
    bar_left = 20
    hours_day = END_DAY - BEGIN_DAY
    per_hour = math.floor((epd7in5.EPD_HEIGHT - bar_top - offset_top) / hours_day)
    per_day = math.floor((width - bar_left - offset_left) / DAYS)
    
    text_size = 15

    print("DAYS: {}".format(DAYS))
    print("hours_day: {}".format(hours_day))
    print("per_hour: {}\t lost: {}".format(per_hour, height - bar_top - offset_top - hours_day * per_hour))
    print("per_day: {}\t lost: {}".format(per_day, width - bar_left - offset_left - per_day * DAYS))
#    conf = configparser.ConfigParser()
#    conf.read("config.ini")
#
#    url = conf['DEFAULT']['URL']
#
    epd = epd7in5.EPD()
#
#    start = datetime.datetime.now()
#    end = start + datetime.timedelta(days=100)
#
#    evs = events(url, start=start, end=end)
#
#    evs.sort()
#
    im = Image.new('1', (epd7in5.EPD_WIDTH, epd7in5.EPD_HEIGHT), 255)
    d = ImageDraw.Draw(im)
    ftext = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Light.ttf', text_size)
    fawesome = ImageFont.truetype('fa-regular.otf', text_size)
    
    # separate top bar from rest
    d.line([(offset_left, offset_top + bar_top - 1), (epd7in5.EPD_WIDTH, offset_top + bar_top - 1)], width=2)
    # separate the left bar from the rest
    d.line([(offset_left + bar_left -1, offset_top), (offset_left + bar_left - 1, height)], width=2)

    # draw the vertical day separators
    for i in range(0, DAYS):
        x = offset_left + bar_left + per_day * i
        if i > 0: 
            d.line([(x, offset_top), (x, height)])
        day = datetime.datetime.today() + datetime.timedelta(days=i)
        headline = day.strftime('%a, %d')
        textsize_x = d.textsize(headline, ftext)[0]
        textoffs_x = math.floor((per_day - textsize_x) / 2)
        d.text((x + textoffs_x, offset_top), headline, font=ftext) 
    
    # draw horizontal hour separators
    for i in range(0, hours_day):
        #d.line([(offset_left + bar_left, offset_top + bar_top + per_hour * i), (width, offset_top + bar_top + per_hour * i)])
        y = offset_top + bar_top + per_hour * i
        if i > 0:
            for j in range(offset_left, width, 4):
                d.point([(j, y)])
        textoffs_y = math.floor((per_hour - text_size) / 2)
        d.text((offset_left, y + textoffs_y - 1), "%02d" % (BEGIN_DAY + i), font=ftext)
    
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
    

