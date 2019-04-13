# epaper-calendar
RasPi-powered e-paper calendar using python and Waveshare's 7.5" e-paper display

## How to use
The calendar data is pulled from the internet via an iCal Link. This link has to be provided in a `config.ini` file:
```
[DEFAULT]
URL=https://url.com/calendar/123
```
Replace the URL with you calendar's file and place it alongside the python files.
