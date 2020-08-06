import datetime

DEFAULT_TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
HONG_KONG_TIMEZONE = "Asia/Hong_Kong"
TEXTWRAP_SEPARATOR = "\n\t\t          "
NUMBER_OF_MESSAGES_USED_TO_FIND_TEMPLATE = 200
REFRESH_ORDER_STATUS_SECOND_INTERVAL = 0.2
GITHUB_REPO_LINK = "https://github.com/tfhkzp/telegram_follow_trader"
DISCLAIMER_LINK = "https://raw.githubusercontent.com/tfhkzp/telegram_follow_trader/master/disclaimer.txt"
DISCLAIMER_API_LINK = "https://api.github.com/repos/tfhkzp/telegram_follow_trader/contents/disclaimer.txt"
SAVE_TELEGRAM_LOGIN_INFORMATION = False

WINDOWS_DIR_PATH = ''
MAC_DIR_PATH = 'Library/Application Support/TelegramFollowTrader/'
MAC_PLATFORM_NAME = "darwin"


class TradeAction:
    OPEN = "OPEN"
    CLOSE = "CLOSE"


class TradeDirection:
    BUY = "BUY"
    SELL = "SELL"


TRADE_POSITION_DESCRIPTION = {
    None: "沒有",
    TradeDirection.BUY: "好倉",
    TradeDirection.SELL: "淡倉"
}

TRADE_DIRECTION_DESCRIPTION = {
    TradeDirection.BUY: "買入",
    TradeDirection.SELL: "賣出"
}


class TradeMode:
    FIXED_QUANTITY = "FIXED_QUANTITY"
    MAX_QUANTITY = "MAX_QUANTITY"


class TradePeriod:
    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    NIGHT = "NIGHT"


class TradePeriodTime:
    MORNING_START_TIME = datetime.time(9, 15, 0)
    MORNING_END_TIME = datetime.time(12, 0, 0)
    AFTERNOON_START_TIME = datetime.time(13, 0, 0)
    AFTERNOON_END_TIME = datetime.time(16, 30, 0)
    NIGHT_START_TIME = datetime.time(17, 15, 0)
    NIGHT_END_TIME = datetime.time(3, 0, 0)


class TradeProductCode:
    HSI = "HSI"
    MHI = "MHI"


class Color:
    SUCCESS = "#4fb636"
    WARNING = "#ae6833"
    ERROR = "#b6364f"
    INFO = "#008ae6"
    DARK = "#002b36"
    TEXT = "#eee8d5"
    SHARP = "#d3c592"
    TIME_TEXT = "#008080"
    CONSTRAST = "#b58300"


class TkinterTextColorTag:
    class LogTime:
        TITLE = "LOG_TIME"
        FG_COLOR = Color.TIME_TEXT
        BG_COLOR = None

    class Sharp:
        TITLE = "SHARP"
        FG_COLOR = Color.SHARP
        BG_COLOR = None

    class Success:
        TITLE = "SUCCESS"
        FG_COLOR = None
        BG_COLOR = Color.SUCCESS

    class Warning:
        TITLE = "WARNING"
        FG_COLOR = None
        BG_COLOR = Color.WARNING

    class Error:
        TITLE = "ERROR"
        FG_COLOR = None
        BG_COLOR = Color.ERROR

    class Info:
        TITLE = "INFO"
        FG_COLOR = None
        BG_COLOR = Color.INFO


class TkinterEntryType:
    INTEGER = "INTEGER"
    POSITIVE_INTEGER = "POSITIVE_INTEGER"
    FLOAT = "FLOAT"
