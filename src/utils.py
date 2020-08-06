import datetime
import pytz
import constants
import webbrowser
from sys import platform as _platform
import os
import requests
import base64


def get_local_datetime_str_in_default_format():
    return datetime.datetime.now().strftime(constants.DEFAULT_TIME_FORMAT)[:-3]


def get_hong_kong_datetime_str_in_default_format():
    hk_date = get_hong_kong_datetime()
    return hk_date.strftime(constants.DEFAULT_TIME_FORMAT)[:-3]


def get_hong_kong_datetime():
    utc_date = datetime.datetime.utcnow()
    utc_date = utc_date.replace(tzinfo=pytz.UTC)
    hk_date = utc_date.astimezone(pytz.timezone(constants.HONG_KONG_TIMEZONE))
    hk_date = hk_date.replace(tzinfo=None)
    return hk_date


def check_time_in_range(target_time, start_time, end_time):
    if start_time < end_time:
        return start_time < target_time < end_time
    else:
        return start_time < target_time or target_time < end_time


def get_current_trade_period(curr_date):
    curr_time = datetime.time(curr_date.hour, curr_date.minute, curr_date.second)
    if check_time_in_range(curr_time, constants.TradePeriodTime.MORNING_START_TIME,
                           constants.TradePeriodTime.MORNING_END_TIME):
        return constants.TradePeriod.MORNING
    elif check_time_in_range(curr_time, constants.TradePeriodTime.AFTERNOON_START_TIME,
                             constants.TradePeriodTime.AFTERNOON_END_TIME):
        return constants.TradePeriod.AFTERNOON
    elif check_time_in_range(curr_time, constants.TradePeriodTime.NIGHT_START_TIME,
                             constants.TradePeriodTime.NIGHT_END_TIME):
        return constants.TradePeriod.NIGHT
    else:
        return None


def get_utc_trade_period_morning_start_date():
    utc_date = datetime.datetime.utcnow()
    utc_date = utc_date.replace(tzinfo=pytz.UTC)
    hk_date = utc_date.astimezone(pytz.timezone(constants.HONG_KONG_TIMEZONE))
    hk_time = datetime.time(hk_date.hour, hk_date.minute, hk_date.second)
    start_time = constants.TradePeriodTime.MORNING_START_TIME
    end_time = constants.TradePeriodTime.NIGHT_END_TIME
    if check_time_in_range(hk_time, start_time, end_time):
        if hk_time.hour < start_time.hour:
            hk_date = hk_date - datetime.timedelta(days=1)
    utc_trade_start_datetime = hk_date.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second,
                                               microsecond=start_time.microsecond)
    utc_trade_start_datetime = utc_trade_start_datetime.astimezone(pytz.UTC)
    return utc_trade_start_datetime


def convert_symbol_to_code(text):
    l = list(text)
    i = 0
    while i < len(l):
        o = ord(l[i])
        if o > 65535:
            l[i] = "{" + str(o) + "ū}"
        i += 1
    return "".join(l)


def open_link(url):
    webbrowser.open_new(url)


def escape_template_str(template_str):
    if template_str is None:
        return None
    return template_str.translate(str.maketrans({"[": r"\[",
                                                 "]": r"\]",
                                                 "(": r"\(",
                                                 ")": r"\)"
                                                 }))


def get_dir_path_by_platform():
    if _platform == "darwin":
        path = os.path.join(os.path.expanduser("~"), constants.MAC_DIR_PATH)
        if not os.path.exists(path):
            os.mkdir(path)
    else:
        path = constants.WINDOWS_DIR_PATH
    return path


def get_disclaimer_version_and_content():
    version = None
    content = None
    try:
        req = requests.get(constants.DISCLAIMER_API_LINK)
        if req.status_code == requests.codes.ok:
            req = req.json()
            version = req['sha']
            content = base64.b64decode(req['content'])
            content = content.decode("utf-8")
    finally:
        return version, content
