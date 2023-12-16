import asyncio
from datetime import datetime as dt
import calendar
import json
import requests
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from pyodide.http import pyfetch
from js import console
import datetime

now = dt.now().astimezone()

async def get_next_event():
    CORS_PROXY = "https://corsproxy.io/?" 
    # page = await pyfetch(CORS_PROXY+"https://openrss.org/www.meetup.com/thaipy-bangkok-python-meetup/events/", 
    #                    headers={"Accept": "application/rss+xml"}, mode="no-cors")
    url = CORS_PROXY+"https://www.meetup.com/thaipy-bangkok-python-meetup/events/"
    console.log(url)
    page = await pyfetch(url, mode="cors")
    text = (await page.bytes()).decode("utf8")
    top, rest = text.split('<script id="__NEXT_DATA__" type="application/json">', 1)
    script, _ = rest.split("</script>", 1)
    data = json.loads(script)
    props = data['props']['pageProps']['__APOLLO_STATE__']
    withdates = (p for p in props.values() if hasattr(p, 'get') and p.get(u'dateTime'))
    nextdate = sorted((parse(p['dateTime']),p['title']) for p in withdates)[0]
    return nextdate

async def get_next_repeat():
    next_date = calendar.Calendar(3).monthdatescalendar(now.year, now.month)[3][0]
    if next_date < now.date():
        next_date = calendar.Calendar(3).monthdatescalendar(now.year, now.month+1)[3][0]
    return (dt(next_date.year, next_date.month, next_date.day, 18, 30, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=7))), "")

async def main():
    try:
        next_date, next_event = await get_next_event()
    except Exception as e:
        console.log(str(e))
    next_date, next_event = await get_next_repeat()
    
    output_year = f"{next_date.strftime('%a %b %d')}"
    Element("newdate").write(output_year)
    while True:
        td = relativedelta(next_date, now)

        output = (
            "- in "
            #f"{td.months} month{'' if td.months == 1 else 's'} "
            f"{td.days} day{'' if td.days == 1 else 's'} "
            f"{td.hours} hour{'' if td.hours == 1 else 's'} "
            f"{td.minutes} minute{'' if td.minutes == 1 else 's'} "
            f"{td.seconds} second{'' if td.seconds == 1 else 's'}"
        )
        Element("showtime").write(output)
        Element("title").write(next_event)

        await asyncio.sleep(1)

asyncio.ensure_future(main())
              # Feeds - 