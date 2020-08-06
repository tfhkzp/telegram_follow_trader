import os
from configparser import RawConfigParser
import constants
import utils


class Config(RawConfigParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.disclaimer_section_header = "disclaimer"
        self.telegram_section_header = "telegram"
        self.telegram_dialog_section_header = "telegram_dialog_setting"
        self.trade_account_section_header = "trade_account_setting"
        self.trade_section_header = "trade_setting"
        self.telegram_dialog_setting_prefix = "telegram_dialog_"
        self.file_path = utils.get_dir_path_by_platform() + "setting.ini"
        self.create_setting_file_when_not_exists()
        self.read(self.file_path)

    def create_setting_file_when_not_exists(self):
        if not os.path.exists(self.file_path):
            self[self.disclaimer_section_header] = {
                'disclaimer_version': 'LOCAL',
                'understand_and_agree': 'N'
            }
            self[self.telegram_section_header] = {
                'api_id': '',
                'api_hash': '',
                'phone_number': ''
            }
            self[self.telegram_dialog_section_header] = {
                'default_dialog_id': ''
            }
            self[self.trade_account_section_header] = {
                'port': 11111
            }
            self[self.trade_section_header] = {
                'trade_mode': constants.TradeMode.FIXED_QUANTITY,
                'trade_product_hsi': 'Y',
                'trade_product_mhi': 'N',
                'hsi_trade_quantity': 1,
                'mhi_trade_quantity': 1,
                'hsi_margin': 150000,
                'mhi_margin': 30000,
                'trade_period_morning': 'Y',
                'trade_period_afternoon': 'Y',
                'trade_period_night': 'Y',
                'open_extra_price': 0,
                'close_price_adjust_interval': 1,
                'cancel_unfulfilled_order_after_second': 10,
                'trade_only_within_second': 3,
                'manual_confirm_trade_message': 'Y'
            }
            self.save()

    def get(self, section, code):
        try:
            return super().get(section, code)
        except:
            self.set(section, code, "")
            self.save()
            return ""

    def save(self):
        self.write(open(self.file_path, 'w'))

    def get_disclaimer_version(self):
        return self.get(self.disclaimer_section_header, "disclaimer_version")

    def save_disclaimer_version(self, value):
        self.set(self.disclaimer_section_header, "disclaimer_version", value)
        self.save()

    def get_disclaimer_understand_and_agree(self):
        return self.get(self.disclaimer_section_header, "understand_and_agree")

    def save_disclaimer_understand_and_agree(self, value):
        self.set(self.disclaimer_section_header, "understand_and_agree", value)
        self.save()

    def save_telegram_dialog_setting(self, dialog_id, open_buy_template, close_buy_template, open_sell_template,
                                     close_sell_template, time_format):
        self[self.telegram_dialog_setting_prefix + str(dialog_id)] = {
            'open_buy_template': open_buy_template,
            'close_buy_template': close_buy_template,
            'open_sell_template': open_sell_template,
            'close_sell_template': close_sell_template,
            'time_format': time_format
        }

    def get_telegram_dialog_setting(self, dialog_id):
        try:
            section_header = self.telegram_dialog_setting_prefix + str(dialog_id)
            open_buy_template = self.get(section_header, 'open_buy_template')
            close_buy_template = self.get(section_header, 'close_buy_template')
            open_sell_template = self.get(section_header, 'open_sell_template')
            close_sell_template = self.get(section_header, 'close_sell_template')
            time_format = self.get(section_header, 'time_format')
            return {
                'open_buy_template': open_buy_template,
                'close_buy_template': close_buy_template,
                'open_sell_template': open_sell_template,
                'close_sell_template': close_sell_template,
                'time_format': time_format
            }
        except:
            return None

    def get_default_telegram_dialog_id(self):
        return self.get(self.telegram_dialog_section_header, "default_dialog_id")

    def save_default_telegram_dialog_id(self, value):
        self.set(self.telegram_dialog_section_header, "default_dialog_id", value)
        self.save()

    def get_trade_port(self):
        return self.get(self.trade_account_section_header, "port")

    def save_trade_port(self, value):
        self.set(self.trade_account_section_header, "port", value)
        self.save()

    def get_telegram_setting(self, code):
        return self.get(self.telegram_section_header, code)

    def set_telegram_setting(self, code, value):
        self.set(self.telegram_section_header, code, value)

    def get_trade_setting(self, code):
        return self.get(self.trade_section_header, code)

    def set_trade_setting(self, code, value):
        self.set(self.trade_section_header, code, value)
