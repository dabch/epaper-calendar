#!/usr/bin/python3

from icalevents.icalevents import events
from dateutil.parser import parse
import datetime
import configparser

import epd7in5
from PIL import Image, ImageDraw, ImageFont

if __name__ == "__main__":

    conf = configparser.ConfigParser()
    conf.read("config.ini")

    url = conf['DEFAULT']['URL']

    epd = epd7in5.EPD()

    start = datetime.datetime.now()
    end = start + datetime.timedelta(days=100)

    evs = events(url, start=start, end=end)

    evs.sort()

    i = Image.new('1', (epd7in5.EPD_WIDTH, epd7in5.EPD_HEIGHT), 255)
    d = ImageDraw.Draw(i)
    f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Light.ttf', 15)
    fawesome = ImageFont.truetype('fa-regular.otf', 15)

    logostr = ''
    evstr = ''
    for e in evs:
        title = e.summary
        #begin = e.start
        #end = e.end
        left = e.time_left()
        if left.total_seconds() > 0: # event in future
            if left.days > 0:
                leftstr = "{} days".format(left.days)
            elif left.seconds <= 3600: # more than one hour in future
                leftstr = "next hour"
            else:
                hours = left.seconds / 3600
                leftstr = "{} hours".format(hours)
        else: # event has started
            to_end = 


    print(evstr)

    #d.text((0,  0), logostr, font=fawesome)
    #d.text((20, 0), evstr, font=f)

#    epd.init()
#    epd.display(epd.getbuffer(i))
#    epd.sleep()



