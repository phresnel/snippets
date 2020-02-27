from sys import argv
import datetime as dt
import calendar
from datetime import datetime
from dateutil import parser
import re

from datetime_helpers import *


def convert_to_timedelta(delta_string):
    parts = re.finditer(r'([+-]?\d+)(\D+?)', delta_string) # normalize and split again
    delta = dt.timedelta()

    units = [
        (['s', 'sec', 'secs', 'second', 'seconds'], dt.timedelta(seconds=1)),
        (['m', 'min', 'mins', 'minute', 'minutes'], dt.timedelta(minutes=1)),
        (['h', 'hrs', 'hour', 'hours'],             dt.timedelta(hours=1)),
        (['d', 'day', 'days'],                      dt.timedelta(days=1)),
        (['w', 'wk', 'wks', 'week', 'weeks'],       dt.timedelta(weeks=1))
    ]

    for s in parts:
        quantity = int(s.group(1))

        for unit in units:
            if s.group(2) in unit[0]:
                delta += unit[1] * quantity
                break
        else:
            raise Exception("Cannot do anything with value {0}".format(s))

    return delta


def parse_info(when, now):
    when_info = parser.parser()._parse(when)
    info = {
        "day"   : hasattr(when_info, 'day')      and when_info.day!=None,
        "month" : hasattr(when_info, 'month')    and when_info.month!=None,
        "year"  : hasattr(when_info, 'year')     and when_info.year!=None,
        "hour"  : hasattr(when_info, 'hour')     and when_info.hour!=None,
        "minute"  : hasattr(when_info, 'minute') and when_info.minute!=None,
        "second"  : hasattr(when_info, 'second') and when_info.second!=None,
        "microsecond" : hasattr(when_info, 'microsecond') and when_info.microsecond!=None,
    }
    info["no_date"] = not info["day"] and not info["month"] and not info["year"]
    return info


def function_with_bad_name(now, when, asking_since=False):
    info = parse_info(when, now)
    when = parser.parse(when, default=now)

    towards_past   = now > when
    towards_future = not towards_past

    def only(*keys):
        ret = True
        for i in keys:
            ret = ret and (not True in [v for (k,v) in info.iteritems() 
                                        if k not in keys]
                           and info[i])
        return ret

    # Handle special case with month only.
    # Difference to current month is 0.
    # Difference to previous months is in relation to end of month.
    # Difference to upcoming months is in relation to beginning of month.
    if only('month','year'):
        if now.month == when.month and now.year == when.year:
            return now
        elif towards_past:
            return end_of_month(when)
        else:
            return beginning_of_month(when)

    if only('month'):
        if now.month == when.month:
            return now
        elif towards_past:
            return (end_of_month(when) if asking_since
                    else beginning_of_month(increment_year(when)))
        else:
            return (end_of_month(decrement_year(when)) if asking_since
                    else beginning_of_month(when))

    if asking_since:
        if towards_past:
            return when
        else:
            if only('day'):            return decrement_month(when)
            elif only('day', 'month'): return decrement_year(when)
            elif info["no_date"]:      return when - dt.timedelta(days=1)
    else:
        if towards_future:
            return when
        else:
            if only('day'):            return increment_month(when)
            elif only('day', 'month'): return increment_year(when)
            elif info["no_date"]:      return when + dt.timedelta(days=1)

    raise Exception("unrecognized partial date")


def convert_to_datetime(args, now=datetime.now(), asking_since=False):
    joined = ' '.join(args)
    joined = joined.lower()

    if joined in ["tomorrow"]:
        return datetime.combine(dt.date.today(), dt.time()) + dt.timedelta(days=1)
    elif joined in ["yesterday"]:
        return datetime.combine(dt.date.today(), dt.time())
    elif joined in ["midnight"]:
        last_midnight = datetime.combine(dt.date.today(), dt.time())
        if asking_since: return last_midnight
        else: return last_midnight + dt.timedelta(days=1)
    elif joined in ["noon"]:
        last_noon = datetime.combine(dt.date.today(), dt.time(12,0))
        if asking_since: return last_noon
        else: return last_midnight + dt.timedelta(days=1)
    else:
        return function_with_bad_name(now, joined,
                                      asking_since=asking_since)


def print_help():
    pass


# Ideas:
#  "now in <timedelta>"
#  "now to/until <datetime>"
#  "now to/until <special-dateimte>", with special-datetime: end-of-month, etc.
#  "now whats <datetime> [in <timezone>]"
# TODO:
#  - eliminate race conditions at midnight
#  - fails for 'now [in|till] monday'
# Do not forget daylight saving times.
def main():
    del argv[0] # don't need
    now = datetime.now()

    if len(argv) == 0:
        print dt.datetime.now()
        return
    elif argv[0] == "in":
        del argv[0]        
        print datetime.now() + convert_to_timedelta(''.join(argv))
    elif argv[-1] == "ago":
        del argv[-1]        
        print datetime.now() - convert_to_timedelta(''.join(argv))
    elif argv[0] in ["to","until","till"]:
        del argv[0]
        lhs = convert_to_datetime(argv, now=now)
        rhs = now
        if lhs>rhs: print lhs-rhs
        else: print '-' + str(rhs-lhs)
    elif argv[0] in ["since","from"]:
        del argv[0]
        lhs = convert_to_datetime(argv, now=now, asking_since=True)
        rhs = now
        if lhs>rhs: print '-' + str(lhs-rhs)
        else: print rhs-lhs
    else:
        print "I am inable to parse that."
        print_help()


if "--devel" in argv:
    argv.remove("--devel")
    main()
else:
    try: 
        main()
    except Exception as e:
        print "Error: {0}".format(e)

