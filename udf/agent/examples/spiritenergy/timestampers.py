import calendar
import datetime
import pytz


def identity_fn(dt):
    '''passes a timestamp through'''
    return dt

#metaprogramming: make datetime canonical return value for instance
class Timestamp(object):
        '''create a new python datetime using stamp_fn'''
        def __init__(self, dt, stamp_fn=identity_fn):
            self._datetime = stamp_fn(dt)

        def adjust(self, amount, unit): 
            '''adjust this timestamp by $amount $units, return self for chaining'''
            keyword = {unit:amount}
            delta = datetime.timedelta(**keyword)
            self._datetime = self._datetime + delta
            return self
        
        def adjusted_by(self, amount, unit):
            '''create and return a new time stamp adjusted by $amount $units'''
            keyword = {unit:amount}
            delta = datetime.timedelta(**keyword)
            return Timestamp(self._datetime + delta)

        def to(self, transform_fn):
            '''create and return a representation of this timestamp using transform_fn'''
            return transform_fn(self._datetime)
        
        def __eq__(self, other):
            if self._datetime == other._datetime:
                return True
            else:
                return False


###transform functions
def influx_ts(ts):
    '''creates an influx timestamp from a Python Datetime'''
    influx_timestamp = calendar.timegm(ts.timetuple()) * 1000000000
    return influx_timestamp

def django_ts(dt): 
    dt = dt.replace(tzinfo=pytz.UTC)
    return dt

def py_ts(dt):
    return dt

###stamp functions. these must return a datetime obect.
def channel4(dt):
    dt = dt.split('T')
    #ignores milliseconds
    params = map(int, dt[0].split('-')) + map(int, dt[1].split('.')[0].split(':'))
    dt = datetime.datetime(*params)
    return dt

def flowmeter(dt):
    d, t = dt.split(' ')
    d = map(int, d.split('/'))
    d = datetime.date(d[2], d[0], d[1])
    t = map(_cast, t.split(':'))
    t = datetime.time(*[x for x in t])
    dt = datetime.datetime.combine(d, t)
    return dt

def denbury(dt):
    d, t = dt
    d = map(int, d.split('/'))
    d = datetime.date(d[2], d[0], d[1])
    t = map(_cast, t.split(':'))
    t = datetime.time(*[x for x in t])
    dt = datetime.datetime.combine(d, t)
    return dt

def memorygauge(dt):
    d, t = dt
    d = map(int, d.split('/'))
    d = datetime.date(d[2], d[0], d[1])
    t = map(_cast, t.split(':'))
    t = datetime.time(*[x for x in t])
    dt = datetime.datetime.combine(d, t)
    return dt


def panax(dt):
    d, t = dt
    d = map(int, d.split('/'))
    d = datetime.date(d[2], d[1], d[0])
    t = map(_cast, t.split(':'))
    t = datetime.time(*[x for x in t])
    dt = datetime.datetime.combine(d, t)
    return dt

def rstamp(date, time): ##todo
    d = map(int, date.split('-'))
    d = datetime.date(d[0], d[1], d[2])
    dt = datetime.datetime.combine(d, t)
    return dt

def exp(dt):
    d,t = dt.split(' ')
    '''assumes a string of the form 6/10/2016 15:33:00'''
    d = map(int, d.split('/'))
    d = datetime.date(d[2], d[0], d[1])
    t = map(int, t.split(':'))
    if len(t) == 2:
        t.append(0)
    t = datetime.time(t[0], t[1], t[2])
    dt = datetime.datetime.combine(d,t)
    return dt

def _cast(numeric_string):
        return int(float(numeric_string))
