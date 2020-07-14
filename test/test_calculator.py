from datetime import datetime
from pytz import timezone
from calculator import is_business_day, is_business_hour, subtract_business_interval
from .sample_calendar import EuronextExchangeCalendar

euronext_cal = EuronextExchangeCalendar()


def test_calendar_is_business_day():
    may_day = datetime(2020, 5, 1)
    business_day = datetime(2020, 4, 30)
    assert (not is_business_day(may_day, euronext_cal))
    assert (is_business_day(business_day, euronext_cal))


def test_calendar_is_business_day_with_df_calendar():
    df_business_calendar = euronext_cal.schedule(start_date='2020-01-01', end_date='2020-10-01')
    may_day = datetime(2020, 5, 1)
    business_day = datetime(2020, 4, 30)
    assert (not is_business_day(may_day, df_business_calendar=df_business_calendar))
    assert (is_business_day(business_day, df_business_calendar=df_business_calendar))


def test_calendar_is_business_hour():
    test_hour_neg = datetime(2020, 4, 30, 1, 30, 33, tzinfo=timezone('UTC'))
    test_hour_pos = datetime(2020, 4, 30, 15, 30, tzinfo=timezone('UTC'))
    assert (not is_business_hour(test_hour_neg, business_calendar=euronext_cal))
    assert (is_business_hour(test_hour_pos, business_calendar=euronext_cal))


def test_calendar_is_business_hour_with_calendar_df():
    business_day = euronext_cal.schedule(start_date='2020-01-01', end_date='2020-10-01')
    test_hour_neg = datetime(2020, 4, 30, 1, 30, 33, tzinfo=timezone('UTC'))
    test_hour_pos = datetime(2020, 4, 30, 15, 00, tzinfo=timezone('UTC'))
    assert (not is_business_hour(test_hour_neg, df_business_calendar=business_day))
    assert (is_business_hour(test_hour_pos, df_business_calendar=business_day))


def test_subtract_business_interval():
    business_cal = EuronextExchangeCalendar()
    input = datetime(2020, 5, 17, 23, 36, tzinfo=timezone('UTC'))
    x = subtract_business_interval(input, business_cal,'1 day', 2)
    assert (x == datetime(2020, 5, 14, 0, 0, tzinfo=timezone('UTC')))

    input = datetime(2020, 5, 17, 23, 36, tzinfo=timezone('UTC'))
    x = subtract_business_interval(input, business_cal, '30 minute', 2)
    assert (x == datetime(2020, 5, 15, 14, 30, tzinfo=timezone('UTC')))