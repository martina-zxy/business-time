from datetime import datetime, timedelta, time
from pandas_market_calendars import MarketCalendar
import pandas as pd
import pytz

MAX_SUBTRACTED_DAYS = 365


class TimeInterval:
    def __init__(self, interval_unit:str=None, interval_value:int=None):
        self.interval_unit: str = interval_unit
        self.interval_value: int = interval_value

    def __str__(self):
        return '{} {}'.format(self.interval_value, self.interval_unit)

    @staticmethod
    def process_interval(str_interval: str):
        i = str_interval.split(' ')
        if len(i) != 2:
            raise Exception('The input string interval is malformed.')
        interval_unit: str = i[1].lower()
        interval_value: int = int(i[0])
        if interval_unit not in ['day', 'minute']:
            raise Exception('Unknown interval unit {}'.format(interval_unit))
        return TimeInterval(interval_unit, interval_value)


def is_business_day(dt: datetime, business_calendar: MarketCalendar=None, df_business_calendar: pd.DataFrame=None):
    """
    Check if the input is a business day
    :param dt: a datetime object
    :param business_calendar: the business calendar to determine if dt is a business day
    :param df_business_calendar: the business calendar dataframe to determine if dt is a business day
    :return:
    """
    if business_calendar is not None:
        return not business_calendar.valid_days(dt, dt).empty

    if not df_business_calendar.empty:
        return dt.date() in df_business_calendar.index.date


def is_business_hour(dt: datetime, business_calendar: MarketCalendar=None, df_business_calendar: pd.DataFrame=None):
    """
    Check if the input is a business hour
    :param dt:
    :param business_calendar: the business calendar to determine if dt is a valid business hour
    :param df_business_calendar: the business calendar dataframe to determine if dt is a business hour
    :return:
    """
    if business_calendar is not None:
        business_day = business_calendar.schedule(start_date=dt.strftime('%Y-%m-%d'), end_date=dt.strftime('%Y-%m-%d'))
        if business_day.empty:
            return False
        return MarketCalendar.open_at_time(business_day, dt, include_close=True)

    if not df_business_calendar.empty:
        df_temp = df_business_calendar.loc[(df_business_calendar['market_open'] <= dt) &
                                           (df_business_calendar['market_close'] > dt)]
        return not df_temp.empty


def round_time(dt, time_interval: TimeInterval):
    """
    Round down a datetime object to a multiple of a timedelta
    :param dt: datetime object
    :param time_interval: TimeInterval object telling to what time granularity dt should be rounded
    :return:
    """
    if time_interval.interval_unit == 'day':
        return dt.replace(hour=0, minute=0, second=0)
    else:
        #  time_interval.interval_unit == 'minute':
        time_delta = timedelta(minutes=time_interval.interval_value)
        round_to = time_delta.total_seconds()
        seconds = dt.timestamp()

        # // is a floor division
        rounding = seconds // round_to * round_to
        return dt + timedelta(0, rounding-seconds, -dt.microsecond)


def subtract_business_interval(end_timestamp: datetime,
                               business_calendar: MarketCalendar,
                               interval: str,
                               nb_valid_interval: int):
    """
    Returns the latest datetime that gives enough timespan from the end_timestamp to
    cover nb_valid_interval of business time intervals. Currently supports days and minutes
    :param end_timestamp: end timestamp of the time period
    :param business_calendar: business calendar to define the business hour
    :param interval: time interval
    :param nb_valid_interval: the number of valid business days interval to cover
    :return:
    """
    interval = TimeInterval.process_interval(interval)
    if interval.interval_unit != 'day' and interval.interval_unit != 'minute':
        raise Exception("Time interval not recognized")

    earliest_start = end_timestamp - timedelta(days=MAX_SUBTRACTED_DAYS)
    df_business_calendar = business_calendar.schedule(start_date=earliest_start.strftime('%Y-%m-%d'),
                                                      end_date=end_timestamp.strftime('%Y-%m-%d'))
    start_timestamp = round_time(end_timestamp, interval).replace(tzinfo=pytz.UTC)

    i = 0
    if (interval.interval_unit == 'day'
            and end_timestamp.time() > time(0, 0, 0)
            and is_business_day(end_timestamp, df_business_calendar=df_business_calendar)) or \
            (interval.interval_unit == 'minute'
            and (end_timestamp - start_timestamp).total_seconds() > 0
            and is_business_hour(end_timestamp, df_business_calendar=df_business_calendar)):
        i += 1

    while i < nb_valid_interval and start_timestamp > earliest_start:
        if interval.interval_unit == 'day':
            start_timestamp = start_timestamp - timedelta(days=interval.interval_value)
            if is_business_day(start_timestamp, df_business_calendar=df_business_calendar):
                i += 1
        else:
            start_timestamp = start_timestamp - timedelta(minutes=interval.interval_value)
            if is_business_hour(start_timestamp, df_business_calendar=df_business_calendar):
                i += 1
    return start_timestamp