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

        print("{}: {} to {} \n\tall_day: {},\n\trecurring: {}\n\tlocation: {}\n\ttime_left: {}\n\tdescription: {}".format(e.summary, e.start, e.end, e.all_day, e.recurring, e.location, e.time_left(), e.description))
        days_duration = e.end.date() - e.start.date() + datetime.timedelta(days=1)
        print("days_duration: {}".format(days_duration))
        if e.end.hour == 0 and e.end.minute == 0:
            days_duration -= datetime.timedelta(days=1)
        print("corrected days_duration: {}".format(days_duration))
        print(days_duration)
    print(evstr)

    #d.text((0,  0), logostr, font=fawesome)
    #d.text((20, 0), evstr, font=f)

#    epd.init()
#    epd.display(epd.getbuffer(i))
#    epd.sleep()



