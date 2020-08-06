from base_trade_app import BaseTradeApp
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import time
import re
import socket
import threading
import asyncio
from telegram_manager import TelegramManager
import traceback
import calendar
from trade_manager import TradeManager
import nest_asyncio
import constants
from styles import UI
import utils
import futu as ft


class App(BaseTradeApp):
    host = "127.0.0.1"
    trade_manager = TradeManager()
    trade_settings = None

    is_handling_trade_record = False
    dialog_active_trade_record_list = []
    dialog_trade_record_queue_list = []

    confirm_trade_message = None
    timer_label = None

    def quit_app(self):
        try:
            if self.tg is not None:
                self.run_async_task(self.tg.logout)
            self.trade_manager.disconnect()
        finally:
            self.app.destroy()
            self.async_loop.stop()

    async def login(self, *args):
        self.disable_elements(self.login_button)
        api_id = self.api_id_entry.get()
        api_hash = self.api_hash_entry.get()
        phone_number = self.phone_number_entry.get()
        try:
            if constants.SAVE_TELEGRAM_LOGIN_INFORMATION:
                self.config.set_telegram_setting("api_id", api_id)
                self.config.set_telegram_setting("api_hash", api_hash)
                self.config.set_telegram_setting("phone_number", phone_number)
                self.config.save()
            self.tg = TelegramManager(api_id, api_hash, phone_number)
            self.tg.login(code_callback=self.get_verification_code, password_callback=self.get_2fa_password)
            await self.start_trade_app()
            self.tg.client.run_until_disconnected()
        except:
            if self.verify_button_var is None or self.verify_button_var.get() != "CANCEL":
                messagebox.showerror("無法登入", "請確認你輸入的資料無誤")
            self.enable_elements(self.login_button)
            traceback.print_exc()
            exit()

    async def get_verification_code(self):
        self.verify_phone_form = tk.Toplevel(self.login_form)
        self.verify_phone_form.transient(self.login_form)
        screenwidth = self.verify_phone_form.winfo_screenwidth()
        screenheight = self.verify_phone_form.winfo_screenheight()
        width = UI.VerificationForm.WIDTH
        height = UI.VerificationForm.HEIGHT
        self.verify_phone_form.grab_set()
        self.verify_phone_form.resizable(False, False)
        self.verify_phone_form.title('輸入驗證碼')

        self.verify_phone_form.geometry('%dx%d+%d+%d' % (width, height,
                                                         (screenwidth / 2) - (width / 2),
                                                         (screenheight / 2) - (height / 2)))

        tk.Label(self.verify_phone_form, text="驗證碼", anchor="w",
                 width=UI.VerificationForm.VERIFICATION_CODE_LABEL_WIDTH) \
            .grid(row=0, column=0, padx=(UI.VerificationForm.PADDING, 0))
        verification_code = tk.StringVar()
        verification_code_entry = tk.Entry(self.verify_phone_form, textvariable=verification_code,
                                           width=UI.VerificationForm.VERIFICATION_CODE_INPUT_WIDTH)
        verification_code_entry.grid(row=0, column=1, padx=(0, UI.VerificationForm.PADDING))
        self.verify_button_var = tk.StringVar()
        verify_button = tk.Button(self.verify_phone_form, text="確定",
                                  command=lambda: self.verify_button_var.set("VERIFY"))
        verify_button.grid(row=1, column=1, sticky="E", padx=(0, UI.VerificationForm.VERIFY_BUTTON_PADDING_X),
                           pady=UI.VerificationForm.VERIFY_BUTTON_PADDING_Y)
        self.verify_phone_form.protocol("WM_DELETE_WINDOW", lambda: self.verify_button_var.set("CANCEL"))
        verify_button.wait_variable(self.verify_button_var)
        verification_code = verification_code_entry.get()
        if self.verify_button_var.get() == "CANCEL":
            self.verify_phone_form.destroy()
            self.verify_phone_form = None
        else:
            self.verify_phone_form.withdraw()
        return verification_code

    async def get_2fa_password(self):
        self.verify_password_form = tk.Toplevel(self.login_form)
        screenwidth = self.verify_password_form.winfo_screenwidth()
        screenheight = self.verify_password_form.winfo_screenheight()
        width = UI.VerificationForm.WIDTH
        height = UI.VerificationForm.HEIGHT
        self.verify_password_form.grab_set()
        self.verify_password_form.resizable(False, False)
        self.verify_password_form.title('輸入密碼')
        self.verify_password_form.geometry('%dx%d+%d+%d' % (width, height,
                                                            (screenwidth / 2) - (width / 2),
                                                            (screenheight / 2) - (height / 2)))

        tk.Label(self.verify_password_form, text="密碼", anchor="w", width=UI.VerificationForm.PASSWORD_LABEL_WIDTH) \
            .grid(row=0, column=0, padx=(UI.VerificationForm.PADDING, 0))
        password_var = tk.StringVar()
        password_entry = tk.Entry(self.verify_password_form, textvariable=password_var,
                                  width=UI.VerificationForm.PASSWORD_INPUT_WIDTH, show="*")
        password_entry.grid(row=0, column=1, padx=(0, UI.VerificationForm.PADDING))
        self.verify_button_var = tk.StringVar()
        verify_button = tk.Button(self.verify_password_form, text="確定",
                                  command=lambda: self.verify_button_var.set("VERIFY"))
        verify_button.grid(row=1, column=1, sticky="E", padx=(0, UI.VerificationForm.VERIFY_BUTTON_PADDING_X),
                           pady=UI.VerificationForm.VERIFY_BUTTON_PADDING_Y)
        self.verify_password_form.protocol("WM_DELETE_WINDOW", lambda: self.verify_button_var.set("CANCEL"))
        verify_button.wait_variable(self.verify_button_var)
        password = password_entry.get()
        self.verify_password_form.destroy()
        return password

    async def start_trade_app(self):
        if self.verify_phone_form is not None:
            self.verify_phone_form.destroy()

        me = await self.tg.get_me()
        self.app_title = f"{self.app_title} - [{me.id}]{me.username}"
        self.load_trade_app_gui()
        self.console_write_line("成功連接Telegram")
        await self.get_telegram_dialogs()
        self.load_trade_app_config()
        self.console_write_line("成功載入交易設定")

    async def get_telegram_dialogs(self):
        self.telegram_dialog_list = await self.tg.get_telegram_dialogs()
        self.dialog_select['values'] = tuple(
            utils.convert_symbol_to_code(dialog['title']) for dialog in self.telegram_dialog_list)
        self.console_write_line("成功獲取Telegram用戶頻道列表")

    async def refresh_dialog_list(self, *args):
        self.disable_elements(self.dialog_update_button)
        await self.get_telegram_dialogs()
        if self.selected_dialog_id is not None:
            telegram_dialog_id_list = [dialog['id'] for dialog in self.telegram_dialog_list]
            if self.selected_dialog_id in telegram_dialog_id_list:
                dialog_index = telegram_dialog_id_list.index(self.selected_dialog_id)
                self.dialog_select.current(dialog_index)
        self.dialog_update_button.after(100, self.enable_elements(self.dialog_update_button))

    async def test_dialog_setting(self, *args):
        self.disable_elements(self.dialog_test_button)
        valid, message = await self.validate_dialog_setting()
        title = "頻道設定測試"
        if valid:
            messagebox.showinfo(title, message)
        else:
            messagebox.showerror(title, message)
        self.dialog_test_button.after(100, self.enable_elements(self.dialog_test_button))

    def get_trade_record_template_list(self):
        pattern = r'\${(\w+)}'
        match = r'(?P<\1>.*)'
        open_buy_template = utils.escape_template_str(self.open_buy_template_entry.get().strip())
        close_buy_template = utils.escape_template_str(self.close_buy_template_entry.get().strip())
        open_sell_template = utils.escape_template_str(self.open_sell_template_entry.get().strip())
        close_sell_template = utils.escape_template_str(self.close_sell_template_entry.get().strip())
        time_format = self.time_format_entry.get()
        templates = [
            {
                'description': '建好倉訊息',
                'direction': constants.TradeDirection.BUY,
                'action': constants.TradeAction.OPEN,
                'pattern': re.sub(pattern, match, open_buy_template),
                'time_format': time_format,
                'exist': False,
                'time_valid': False,
                'price_valid': False,
                'month_or_product_code_valid': False,
                'has_trade_id': False
            },
            {
                'description': '平好倉訊息',
                'direction': constants.TradeDirection.SELL,
                'action': constants.TradeAction.CLOSE,
                'pattern': re.sub(pattern, match, close_buy_template),
                'time_format': time_format,
                'exist': False,
                'time_valid': False,
                'price_valid': False,
                'month_or_product_code_valid': False,
                'has_trade_id': False
            },
            {
                'description': '建淡倉訊息',
                'direction': constants.TradeDirection.SELL,
                'action': constants.TradeAction.OPEN,
                'pattern': re.sub(pattern, match, open_sell_template),
                'time_format': time_format,
                'exist': False,
                'time_valid': False,
                'price_valid': False,
                'month_or_product_code_valid': False,
                'has_trade_id': False
            },
            {
                'description': '平淡倉訊息',
                'direction': constants.TradeDirection.BUY,
                'action': constants.TradeAction.CLOSE,
                'pattern': re.sub(pattern, match, close_sell_template),
                'time_format': time_format,
                'exist': False,
                'time_valid': False,
                'price_valid': False,
                'month_or_product_code_valid': False,
                'has_trade_id': False
            }
        ]
        return templates

    @staticmethod
    def validate_dialog_message(template, text, curr_month=None, next_month=None, curr_product_code_month=None,
                                next_product_code_month=None):
        trade_record = None
        if text is not None and template['exist'] is False:
            pattern_match = re.match(template['pattern'], text)
            if pattern_match is not None:
                template['exist'] = True
                trade_record = pattern_match.groupdict()
                if "price" in trade_record:
                    try:
                        price = int(trade_record['price'])
                        if price > 0:
                            template['price_valid'] = True
                    except:
                        pass
                if "time" in trade_record:
                    try:
                        datetime.strptime(trade_record['time'], template['time_format'])
                        template['time_valid'] = True
                    except:
                        pass
                if "trade_id" in trade_record:
                    template['has_trade_id'] = True
                if "product_code" in trade_record:
                    try:
                        product_code = trade_record['product_code'].strip()
                        if len(product_code) == 7 and \
                                (product_code.startswith('HSI') or product_code.startswith('MHI')) and \
                                (product_code.endswith(curr_product_code_month) or product_code.endswith(
                                    next_product_code_month)):
                            template['month_or_product_code_valid'] = True
                    except:
                        pass
                elif "month" in trade_record:
                    try:
                        month = int(trade_record['month'])
                        if month == curr_month or month == next_month:
                            template['month_or_product_code_valid'] = True
                    except:
                        pass
        return template, trade_record

    async def validate_dialog_setting(self):
        open_buy_template = self.open_buy_template_entry.get()
        close_buy_template = self.close_buy_template_entry.get()
        open_sell_template = self.open_sell_template_entry.get()
        close_sell_template = self.close_sell_template_entry.get()
        time_format = self.time_format_entry.get()
        if open_buy_template == "" or \
                close_buy_template == "" or \
                open_sell_template == "" or \
                close_sell_template == "" or \
                time_format == "":
            return False, "請填入所有訊息格式"
        template_set = {open_buy_template, close_buy_template, open_sell_template, close_sell_template}
        if len(template_set) != 4:
            return False, "訊息格式不能相同"

        templates = self.get_trade_record_template_list()
        curr_month, next_month, curr_product_code_month, next_product_code_month = \
            get_current_next_month_and_product_code_month()

        messages_count = constants.NUMBER_OF_MESSAGES_USED_TO_FIND_TEMPLATE
        message_list = await self.tg.get_selected_dialog_recent_messages(self.selected_dialog_id, messages_count)
        template_to_be_checked = [*templates]
        for message in message_list:
            for template in template_to_be_checked:
                self.validate_dialog_message(template, message.text, curr_month, next_month, curr_product_code_month,
                                             next_product_code_month)
                if template['exist'] is True:
                    template_to_be_checked.remove(template)
                    break
            if len(template_to_be_checked) == 0:
                break

        error_message = ""

        for template in templates:
            if template['exist'] is False:
                error_message += f"最近的訊息中找不到{template['description']}\n"
            else:
                if template['price_valid'] is False:
                    error_message += f"{template['description']}: 價格錯誤\n"
                if template['time_valid'] is False:
                    error_message += f"{template['description']}: 時間錯誤\n"
                if template['month_or_product_code_valid'] is False:
                    error_message += f"{template['description']}: 月份或產品編號錯誤\n"
                if template['has_trade_id'] is False:
                    error_message += f"{template['description']}: 沒有交易編號\n"
        if error_message == "":
            return True, f"成功於最近的{messages_count}條訊息記錄找到所有格式"
        else:
            return False, error_message

    async def validate_trade_account_setting(self, connect_trade_client=False):
        trade_password_length = 6
        trade_password = self.trade_password_entry.get()
        port = self.trade_port_entry.get()
        if port != "":
            try:
                port = int(port)
                if port > 65535 or port < 0:
                    return False, "端口超出範圍"
            except:
                return False, "端口必須為數字"
        else:
            return False, "請輸入端口"

        if len(trade_password) != trade_password_length:
            return False, f"請輸入{trade_password_length}位的交易密碼"
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        check_connection_res = a_socket.connect_ex((self.host, port))
        if check_connection_res == 0:
            return self.trade_manager.unlock_trade_password(self.host, port, trade_password, connect_trade_client)
        else:
            return False, f"請先開啟FutuOpenD並設定地址為{self.host}及端口為{port}"

    async def test_trade_account_setting(self, *args):
        self.disable_elements(self.trade_password_test_button)
        valid, message = await self.validate_trade_account_setting()
        title = "交易帳戶測試"
        if valid:
            messagebox.showinfo(title, message)
        else:
            messagebox.showerror(title, message)
        self.trade_password_test_button.after(100, self.enable_elements(self.trade_password_test_button))

    async def validate_trade_setting(self, *args):
        error_message = ""
        trade_settings = self.get_raw_trade_settings()
        trade_mode = trade_settings['trade_mode']
        trade_product_hsi = trade_settings['trade_product_hsi']
        trade_product_mhi = trade_settings['trade_product_mhi']
        hsi_trade_quantity = trade_settings['hsi_trade_quantity']
        mhi_trade_quantity = trade_settings['mhi_trade_quantity']
        hsi_margin = trade_settings['hsi_margin']
        mhi_margin = trade_settings['mhi_margin']
        trade_period_morning = trade_settings['trade_period_morning']
        trade_period_afternoon = trade_settings['trade_period_afternoon']
        trade_period_night = trade_settings['trade_period_night']
        open_extra_price = trade_settings['open_extra_price']
        close_price_adjust_interval = trade_settings['close_price_adjust_interval']
        cancel_unfulfilled_order_after_second = trade_settings['cancel_unfulfilled_order_after_second']
        trade_only_within_second = trade_settings['trade_only_within_second']
        manual_confirm_trade_message = trade_settings['manual_confirm_trade_message']
        if trade_mode is None or (
                trade_mode != constants.TradeMode.FIXED_QUANTITY and trade_mode != constants.TradeMode.MAX_QUANTITY):
            error_message += "請選擇交易模式\n"
        if trade_product_hsi is False and trade_product_mhi is False:
            error_message += "請選擇交易產品\n"
        if trade_period_morning is False and trade_period_afternoon is False and trade_period_night is False:
            error_message += "請選擇交易時段\n"
        if trade_mode == constants.TradeMode.FIXED_QUANTITY:
            if trade_product_hsi:
                try:
                    hsi_trade_quantity = int(hsi_trade_quantity)
                    if hsi_trade_quantity == 0:
                        error_message += "期貨交易數量不能為0\n"
                except:
                    error_message += "請輸入期貨交易數量\n"
            if trade_product_mhi:
                try:
                    mhi_trade_quantity = int(mhi_trade_quantity)
                    if mhi_trade_quantity == 0:
                        error_message += "小型期貨交易數量不能為0\n"
                except:
                    error_message += "請輸入小型期貨交易數量\n"
        elif trade_mode == constants.TradeMode.MAX_QUANTITY:
            if trade_product_hsi:
                try:
                    hsi_margin = int(hsi_margin)
                    if hsi_margin == 0:
                        error_message += "期貨保證金不能為0\n"
                except:
                    error_message += "請輸入期貨保證金\n"
            if trade_product_mhi:
                try:
                    mhi_margin = int(mhi_margin)
                    if mhi_margin == 0:
                        error_message += "小型期貨保證金不能為0\n"
                except:
                    error_message += "請輸入小型期貨保證金\n"
        try:
            int(open_extra_price)
        except:
            error_message += "請輸入建倉追價\n"
        try:
            close_price_adjust_interval = int(close_price_adjust_interval)
            if close_price_adjust_interval == 0:
                error_message += "平倉調整價格區間不能為0\n"
        except:
            error_message += "請輸入平倉調整價格區間\n"
        try:
            float(cancel_unfulfilled_order_after_second)
        except:
            error_message += "請設定於幾秒後取消未成交建倉訂單\n"
        try:
            float(trade_only_within_second)
        except:
            error_message += "請設定忽略延誤幾秒以上的訊息\n"
        if error_message != "":
            return False, error_message
        else:
            return True, ""

    async def start_follow_trade(self, *args):
        self.disable_elements_on_start_follow_trade()

        def handle_validation_result(title, v, m):
            if v:
                self.console_write_text("正確", constants.TkinterTextColorTag.Success.TITLE, is_end=True)
            else:
                self.console_write_text("錯誤", constants.TkinterTextColorTag.Error.TITLE, is_end=True)
                messagebox.showerror(title, m)

        self.disable_elements(self.start_follow_trade_button)
        self.clear_console()
        self.console_write_line("正在檢查設定...")
        valid, message = await self.validate_dialog_setting()
        self.console_write_text("頻道設定: ", is_start=True)
        handle_validation_result("頻道設定", valid, message)
        if valid:
            self.console_write_text("交易帳戶: ", is_start=True)
            valid, message = await self.validate_trade_account_setting(connect_trade_client=True)
            handle_validation_result("交易帳戶設定", valid, message)
        if valid:
            self.console_write_text("交易設定: ", is_start=True)
            valid, message = await self.validate_trade_setting()
            handle_validation_result("交易設定", valid, message)
        if valid is False:
            self.console_write_line("請檢查設定後再次嘗試")
            self.enable_elements_on_stop_follow_trade()
        else:
            self.console_write_line("通過所有設定檢查")
            self.cache_trade_settings()
            trade_settings = self.trade_settings
            trade_setting_message = "交易設定: "
            trade_setting_message += f"頻道: [{self.selected_dialog_id}]{self.telegram_dialog_list[self.dialog_select.current()]['title']}\n"
            trade_mode_desp = "固定數量" if trade_settings[
                                            'trade_mode'] == constants.TradeMode.FIXED_QUANTITY else "自動檢測最大交易數量"
            trade_setting_message += f"\t\t\t\t交易模式: {trade_mode_desp}\n"
            trade_product_str = ""
            if trade_settings['trade_product_hsi']:
                trade_product_str = "恆生指數期貨"
            if trade_settings['trade_product_mhi']:
                if trade_product_str != "":
                    trade_product_str += ", "
                trade_product_str += "小型恆生指數期貨"
            trade_setting_message += f"\t\t\t\t交易產品: {trade_product_str}\n"

            trade_period_str = ""
            if trade_settings['trade_period_morning']:
                if trade_period_str != "":
                    trade_period_str += ", "
                trade_period_str += "上午"
            if trade_settings['trade_period_afternoon']:
                if trade_period_str != "":
                    trade_period_str += ", "
                trade_period_str += "下午"
            if trade_settings['trade_period_night']:
                if trade_period_str != "":
                    trade_period_str += ", "
                trade_period_str += "晚上"
            trade_setting_message += f"\t\t\t\t交易時段: {trade_period_str}\n"
            hsi_trade_quantity_desp = trade_settings['hsi_trade_quantity'] if \
                trade_settings['trade_mode'] == constants.TradeMode.FIXED_QUANTITY and \
                trade_settings['trade_product_hsi'] is True else "不適用"
            mhi_trade_quantity_desp = trade_settings['mhi_trade_quantity'] \
                if trade_settings['trade_mode'] == constants.TradeMode.FIXED_QUANTITY and \
                   trade_settings['trade_product_mhi'] is True else "不適用"
            trade_setting_message += f"\t\t\t\t期貨交易數量: {hsi_trade_quantity_desp}\n"
            trade_setting_message += f"\t\t\t\t小型期貨交易數量: {mhi_trade_quantity_desp}\n"
            hsi_margin_desp = "不適用" if trade_settings['trade_mode'] == constants.TradeMode.FIXED_QUANTITY or \
                                       trade_settings['trade_product_hsi'] is False else \
                trade_settings['hsi_margin']
            trade_setting_message += f"\t\t\t\t每達保證金交易期貨一張: {hsi_margin_desp}\n"

            mhi_margin_desp = "不適用" if trade_settings['trade_mode'] == constants.TradeMode.FIXED_QUANTITY or \
                                       trade_settings['trade_product_mhi'] is False else \
                trade_settings['mhi_margin']
            trade_setting_message += f"\t\t\t\t每達保證金交易小型期貨一張: {mhi_margin_desp}\n"

            trade_setting_message += f"\t\t\t\t建倉追價: {trade_settings['open_extra_price']}\n"
            trade_setting_message += f"\t\t\t\t平倉調整價格區間: {trade_settings['close_price_adjust_interval']}\n"
            trade_setting_message += "\t\t\t\t幾秒後取消未成交的建倉訂單: %.1f\n" % trade_settings[
                'cancel_unfulfilled_order_after_second']
            trade_setting_message += "\t\t\t\t忽略延誤幾秒以上的交易訊息: %.1f\n" % trade_settings['trade_only_within_second']
            manual_confirm_trade_message_desp = "是" if trade_settings[
                                                           'manual_confirm_trade_message'] is True else "否"
            trade_setting_message += f"\t\t\t\t手動確定每筆交易訊息: {manual_confirm_trade_message_desp}"
            self.console_write_line("正在檢測頻道自今天上午交易時段起的持倉狀態...")
            await self.check_dialog_current_direction()
            position_description = constants.TRADE_POSITION_DESCRIPTION[None]
            if len(self.dialog_active_trade_record_list) > 0:
                active_trade_record = self.dialog_active_trade_record_list[0]
                position_description = constants.TRADE_POSITION_DESCRIPTION[active_trade_record['direction']]

            self.console_write_text("當前頻道持倉: ", is_start=True)
            self.console_write_text(position_description, constants.TkinterTextColorTag.Info.TITLE, is_end=True)
            self.console_write_line(trade_setting_message)
            self.console_write_line("正在等待頻道發出交易訊息...")
            self.tg.start_monitor_dialog_messages(self.selected_dialog_id, self.on_receive_dialog_new_message)
            self.start_follow_trade_button['text'] = "停止"
            self.start_follow_trade_button['command'] = self.stop_follow_trade
            order_list = self.trade_manager.get_order_list_by_order_id_list([])
        self.start_follow_trade_button.after(1000, self.enable_elements(self.start_follow_trade_button))

    def stop_follow_trade(self):
        self.dialog_trade_record_queue_list = []
        self.dialog_active_trade_record_list = []
        self.is_handling_trade_record = False
        self.enable_elements_on_stop_follow_trade()
        self.start_follow_trade_button['text'] = "開始"
        self.start_follow_trade_button['command'] = lambda: self.run_async_task(self.start_follow_trade)
        self.console_write_line("停止跟隨交易", constants.TkinterTextColorTag.Sharp.TITLE)
        self.trade_manager.disconnect()
        self.tg.stop_monitor_dialog_messages()

    def cache_trade_settings(self):
        trade_settings = self.get_raw_trade_settings()
        if trade_settings['trade_mode'] == constants.TradeMode.FIXED_QUANTITY:
            trade_settings['hsi_trade_quantity'] = int(trade_settings['hsi_trade_quantity'])
            trade_settings['mhi_trade_quantity'] = int(trade_settings['mhi_trade_quantity'])
        elif trade_settings['trade_mode'] == constants.TradeMode.MAX_QUANTITY:
            trade_settings['hsi_margin'] = int(trade_settings['hsi_margin'])
            trade_settings['mhi_margin'] = int(trade_settings['mhi_margin'])
        trade_settings['open_extra_price'] = int(trade_settings['open_extra_price'])
        trade_settings['close_price_adjust_interval'] = int(trade_settings['close_price_adjust_interval'])
        trade_settings['cancel_unfulfilled_order_after_second'] = float(
            trade_settings['cancel_unfulfilled_order_after_second'])
        trade_settings['trade_only_within_second'] = float(trade_settings['trade_only_within_second'])
        self.trade_settings = trade_settings

    async def check_dialog_current_direction(self):
        self.dialog_active_trade_record_list = []
        utc_start_time = utils.get_utc_trade_period_morning_start_date()
        message_list = await self.tg.get_selected_dialog_messages_after_date(self.selected_dialog_id, utc_start_time)
        open_trade_count = 0
        close_trade_count = 0
        last_open_trade_record = None

        for message in message_list:
            template, trade_record = self.convert_message_to_trade_record(message.text)
            if template is not None and template['exist'] is True:
                if template['action'] == constants.TradeAction.OPEN:
                    open_trade_count += 1
                    last_open_trade_record = trade_record
                elif template['action'] == constants.TradeAction.CLOSE:
                    close_trade_count += 1
        if open_trade_count > close_trade_count:
            self.dialog_active_trade_record_list.append(last_open_trade_record)

    async def on_receive_dialog_new_message(self, text):
        template, trade_record = self.convert_message_to_trade_record(text)
        if trade_record is not None:
            if self.confirm_trade_message is not None:
                self.console_write_line("收到新的交易訊息,將放棄按照交易訊息設立訂單", constants.TkinterTextColorTag.Sharp.TITLE)
                self.confirm_trade_message.destroy()
                self.confirm_trade_message = None
                self.timer_label = None

            self.console_insert_empty_line()
            product_code_description = trade_record['product_code'] if "product_code" in trade_record else "-"
            month_description = trade_record['month'] if "month" in trade_record else "-"

            self.console_write_line(f"收到{trade_record['description']}, 編號: {trade_record['trade_id']}, "
                                    f"價格: {trade_record['price']}, 產品: {product_code_description}, "
                                    f"月份: {month_description},{constants.TEXTWRAP_SEPARATOR} "
                                    f"時間: {trade_record['formatted_time']}")
            self.console_write_line(f'原文: {text}')

            if trade_record['action'] == constants.TradeAction.OPEN:
                self.dialog_active_trade_record_list.append(trade_record)
                if len(self.dialog_active_trade_record_list) > 1:
                    self.console_write_line(
                        f"當前頻道尚未平倉,將延遲處理編號:{trade_record['trade_id']}的{trade_record['description']}")
                    self.dialog_trade_record_queue_list.append(trade_record)
                    return
            elif trade_record['action'] == constants.TradeAction.CLOSE:
                trade_id = trade_record['trade_id']
                self.remove_active_trade_record_by_trade_id(trade_id)
            if self.is_handling_trade_record is True:
                self.console_write_line(f"正在處理其他交易,將延遲處理編號:{trade_record['trade_id']}的{trade_record['description']}")
                self.dialog_trade_record_queue_list.append(trade_record)
            else:
                if self.trade_settings['manual_confirm_trade_message'] is True:
                    await self.manual_handle_trade_record(trade_record)
                else:
                    await self.handle_trade_record(trade_record)
        elif template is not None:
            error_message_list = []
            if template['price_valid'] is False:
                error_message_list.append("價格錯誤")
            if template['time_valid'] is False:
                error_message_list.append("時間錯誤")
            if template['month_or_product_code_valid'] is False:
                error_message_list.append("產品編號或月份有錯")
            self.console_write_line(f"收到交易記錄,但由於以下原因未能正確處理:{'、'.join(error_message_list)}, 原文:[{text}]")

    async def manual_handle_trade_record(self, trade_record, is_deferred_record=False):
        def focus_out_event(event):
            self.confirm_trade_message.focus_force()

        def count_down_and_close(timer_label, second):
            try:
                if timer_label is not None:
                    timer_label['text'] = f'{second}秒後將會自動關閉...'
                    second = second - 1
                    if second >= 0:
                        if self.confirm_trade_message is not None:
                            t = threading.Timer(1, count_down_and_close, args=[timer_label, second])
                            t.daemon = True
                            t.start()
                    else:
                        self.confirm_trade_message.destroy()
                        self.confirm_trade_message = None
                        self.timer_label = None
                        self.console_write_line("時限內未確認交易訊息,將放棄按照交易訊息設立訂單", constants.TkinterTextColorTag.Sharp.TITLE)
            except:
                pass

        def confirm_place_order():
            self.console_write_line("用戶確認按照交易訊息設立訂單", constants.TkinterTextColorTag.Sharp.TITLE)
            self.confirm_trade_message.destroy()
            self.confirm_trade_message = None
            self.timer_label = None

            self.run_async_task(self.handle_trade_record, trade_record, is_deferred_record)

        def close_confirm_trade_message():
            self.console_write_line("用戶放棄按照交易訊息設立訂單", constants.TkinterTextColorTag.Sharp.TITLE)
            self.confirm_trade_message.destroy()
            self.confirm_trade_message = None
            self.timer_label = None

        self.confirm_trade_message = tk.Toplevel(self.app)
        self.confirm_trade_message.bind("<FocusOut>", focus_out_event)
        self.confirm_trade_message.focus_force()
        self.confirm_trade_message.lift()
        self.confirm_trade_message.attributes('-topmost', True)
        screenwidth = self.confirm_trade_message.winfo_screenwidth()
        screenheight = self.confirm_trade_message.winfo_screenheight()
        width = UI.ConfirmTradeMessageDialog.WIDTH
        height = UI.ConfirmTradeMessageDialog.HEIGHT
        self.confirm_trade_message.grab_set()
        self.confirm_trade_message.resizable(False, False)
        self.confirm_trade_message.title("確認交易訊息")
        self.confirm_trade_message.geometry('%dx%d+%d+%d' % (width, height,
                                                             (screenwidth / 2) - (width / 2),
                                                             (screenheight / 2) - (height / 2)))
        product_code_description = trade_record['product_code'] if "product_code" in trade_record else "-"
        product_month_description = trade_record['month'] if "month" in trade_record else "-"
        trade_record_text = f"收到{trade_record['description']}, 編號: {trade_record['trade_id']}, 價格: {trade_record['price']}," \
                            f" 產品: {product_code_description}, 月份: {product_month_description}, 時間: {trade_record['formatted_time']}"
        trade_message_label = tk.Label(self.confirm_trade_message, text=trade_record_text + "\n要按照該交易訊息進行交易嗎?",
                                       anchor="nw",
                                       font=self.label_font_style, justify="left", bg="white",
                                       padx=UI.ConfirmTradeMessageDialog.PADDING,
                                       wraplength=UI.ConfirmTradeMessageDialog.WRAP_LENGTH)
        trade_message_label.pack()
        trade_message_label.place(width=UI.ConfirmTradeMessageDialog.LABEL_WIDTH,
                                  height=UI.ConfirmTradeMessageDialog.LABEL_HEIGHT)
        second = 10
        self.timer_label = tk.Label(self.confirm_trade_message, text=f"{second}秒後將會自動關閉...", anchor="nw",
                                    justify="left", bg="white", padx=UI.ConfirmTradeMessageDialog.PADDING)
        self.timer_label.pack()
        self.timer_label.place(width=UI.ConfirmTradeMessageDialog.TIMER_LABEL_WIDTH,
                               height=UI.ConfirmTradeMessageDialog.TIMER_LABEL_HEIGHT,
                               y=UI.ConfirmTradeMessageDialog.TIMER_LABEL_Y)
        count_down_and_close(self.timer_label, second)
        confirm_button = tk.Button(self.confirm_trade_message, text="確定", command=confirm_place_order)
        confirm_button.pack()
        confirm_button.place(height=UI.ConfirmTradeMessageDialog.CONFIRM_BUTTON_HEIGHT,
                             width=UI.ConfirmTradeMessageDialog.CONFIRM_BUTTON_WIDTH,
                             x=UI.ConfirmTradeMessageDialog.CONFIRM_BUTTON_X,
                             y=UI.ConfirmTradeMessageDialog.CONFIRM_BUTTON_Y)
        cancel_button = tk.Button(self.confirm_trade_message, text="取消", command=close_confirm_trade_message)
        cancel_button.pack()
        cancel_button.place(height=UI.ConfirmTradeMessageDialog.CANCEL_BUTTON_HEIGHT,
                            width=UI.ConfirmTradeMessageDialog.CANCEL_BUTTON_WIDTH,
                            x=UI.ConfirmTradeMessageDialog.CANCEL_BUTTON_X,
                            y=UI.ConfirmTradeMessageDialog.CANCEL_BUTTON_Y)

    async def handle_trade_record(self, trade_record, is_deferred_record=False):
        try:
            trade_password = int(self.trade_password_entry.get())
            port = int(self.trade_port_entry.get())
            self.trade_manager.unlock_trade_password(self.host, port, trade_password, True)
            self.is_handling_trade_record = True
            trade_settings = self.trade_settings
            trade_action = trade_record['action']
            hk_date = utils.get_hong_kong_datetime()
            trade_period = utils.get_current_trade_period(hk_date)
            if trade_period is None:
                self.console_write_line("由於現在並非可交易時段,將忽略該交易記錄")
                return
            elif (trade_period == constants.TradePeriod.MORNING and self.trade_settings[
                'trade_period_morning'] is False) or \
                    (trade_period == constants.TradePeriod.AFTERNOON and
                     self.trade_settings['trade_period_afternoon'] is False) or \
                    (trade_period == constants.TradePeriod.NIGHT and self.trade_settings[
                        'trade_period_night'] is False):
                self.console_write_line("你沒有勾選該交易時段,將忽略該交易記錄")
                return
            if trade_action == constants.TradeAction.OPEN:
                delta = abs(hk_date - trade_record['trade_time'])
                delta_in_second = delta.total_seconds()
                if delta_in_second > trade_settings['trade_only_within_second']:
                    self.console_write_line(
                        '由於建倉交易記錄的時間與%s訊息時間相差%.2f秒,將不會進行交易' % (
                            "處理" if is_deferred_record is True else "收到", delta_in_second))
                    return
                is_active = self.check_trade_record_is_active_by_trade_id(trade_record['trade_id'])
                if is_active is False:
                    self.console_write_line(f"由於已收到編號: {trade_record['trade_id']}的平倉指示,將不會進行交易")
                    return
            trade_mode = trade_settings['trade_mode']
            trade_direction = trade_record['direction']
            trade_product_code_month = trade_record['trade_product_code_month']
            trade_product_hsi = trade_settings['trade_product_hsi']
            trade_product_mhi = trade_settings['trade_product_mhi']
            current_position_description = "當前的持倉: "
            hsi_position_on_hand, hsi_quantity_on_hand, mhi_position_on_hand, mhi_quantity_on_hand = self.trade_manager. \
                get_holding_position_and_quantity(trade_product_code_month, trade_product_hsi, trade_product_mhi)
            if trade_product_hsi is True:
                current_position_description += "恆生指數期貨: "
                if hsi_quantity_on_hand == 0:
                    current_position_description += "沒有 "
                else:
                    current_position_description += "%d 張%s" % (hsi_quantity_on_hand,
                                                                constants.TRADE_POSITION_DESCRIPTION[
                                                                    hsi_position_on_hand])
                if trade_product_mhi is False:
                    pass
                else:
                    current_position_description += ", "
            if trade_product_mhi is True:
                current_position_description += "小型恆生指數期貨: "
                if mhi_quantity_on_hand == 0:
                    current_position_description += "沒有"
                else:
                    current_position_description += "%d 張%s" % (mhi_quantity_on_hand,
                                                                constants.TRADE_POSITION_DESCRIPTION[
                                                                    mhi_position_on_hand])
            self.console_write_line(current_position_description)
            if trade_mode == constants.TradeMode.MAX_QUANTITY and \
                    trade_product_hsi is True and trade_product_mhi is True and \
                    hsi_quantity_on_hand > 0 and mhi_quantity_on_hand > 0 and \
                    hsi_position_on_hand != mhi_position_on_hand:
                self.console_write_line("你的恆生指數期貨及小型恆生指數期貨持倉方向不同,將不會進行交易")
                return
            if (trade_action == constants.TradeAction.OPEN and
                ((trade_product_hsi is True and hsi_quantity_on_hand > 0) or
                 (trade_product_mhi is True and mhi_quantity_on_hand > 0))) or \
                    (trade_action == constants.TradeAction.CLOSE and
                     ((hsi_quantity_on_hand == 0 and mhi_quantity_on_hand == 0) or
                      (trade_product_hsi is True and hsi_position_on_hand == trade_direction) or
                      (trade_product_mhi is True and mhi_position_on_hand == trade_direction))):
                self.console_write_line("當前持倉方向與交易記錄不同,將不會進行交易")
                return
            if trade_action == constants.TradeAction.OPEN:
                await self.place_open_position_order(trade_record)
            elif trade_action == constants.TradeAction.CLOSE:
                await self.place_close_position_order(trade_record, hsi_quantity_on_hand, mhi_quantity_on_hand)
        except:
            traceback.print_exc()
        finally:
            self.is_handling_trade_record = False
            if len(self.dialog_trade_record_queue_list) > 0:
                trade_record = self.dialog_trade_record_queue_list[0]
                self.remove_trade_record_from_dialog_trade_record_queue_list(trade_record)
                self.console_insert_empty_line()
                self.console_write_line(f"重新處理編號: {trade_record['trade_id']}的{trade_record['description']}")
                await self.handle_trade_record(trade_record, True)

    async def place_open_position_order(self, trade_record):
        trade_settings = self.trade_settings
        trade_mode = trade_settings['trade_mode']
        trade_product_hsi = trade_settings['trade_product_hsi']
        trade_product_mhi = trade_settings['trade_product_mhi']
        open_extra_price = trade_settings['open_extra_price']
        trade_direction = trade_record['direction']
        trade_product_code_month = trade_record['trade_product_code_month']
        order_id_list = []
        trade_id = trade_record['trade_id']
        price = int(trade_record['price'])
        if trade_direction == constants.TradeDirection.BUY:
            price = price + open_extra_price
        else:
            price = price - open_extra_price
        hsi_quantity = 0
        mhi_quantity = 0
        is_active = self.check_trade_record_is_active_by_trade_id(trade_id)
        if is_active is False:
            self.console_write_line(f"由於已收到編號:{trade_record['trade_id']}的平倉指示,將不會進行交易")
            return
        if trade_mode == constants.TradeMode.MAX_QUANTITY:
            hsi_quantity, mhi_quantity = self.trade_manager.get_max_trade_quantity(
                trade_settings['hsi_margin'], trade_settings['mhi_margin'], trade_product_hsi, trade_product_mhi)
            if hsi_quantity == 0 and mhi_quantity == 0:
                self.console_write_line("當前的可用資金不足,將不會進行交易")
        else:
            if trade_product_hsi is True:
                hsi_quantity = trade_settings['hsi_trade_quantity']
            elif trade_product_mhi is True:
                mhi_quantity = trade_settings['mhi_trade_quantity']
        if hsi_quantity > 0:
            result, order_data, error_message = self.trade_manager.place_order(constants.TradeProductCode.HSI,
                                                                               trade_product_code_month,
                                                                               trade_record['direction'], price,
                                                                               hsi_quantity)
            self.log_place_order_result(result, order_data, error_message, trade_direction, price, hsi_quantity)
            if result is True:
                order_id_list.append(order_data['order_id'])
        if mhi_quantity > 0:
            result, order_data, error_message = self.trade_manager.place_order(constants.TradeProductCode.MHI,
                                                                               trade_product_code_month,
                                                                               trade_record['direction'], price,
                                                                               mhi_quantity)
            self.log_place_order_result(result, order_data, error_message, trade_direction, price, mhi_quantity)
            if result is True:
                order_id_list.append(order_data['order_id'])
        if len(order_id_list) > 0:
            cancel_unfulfilled_order_after_second = trade_settings['cancel_unfulfilled_order_after_second']
            max_refresh_count = round(
                cancel_unfulfilled_order_after_second / constants.REFRESH_ORDER_STATUS_SECOND_INTERVAL)
            refresh_count = 0
            hsi_completed = False if hsi_quantity > 0 else True
            mhi_completed = False if mhi_quantity > 0 else True
            current_hsi_dealt_quantity = 0
            current_mhi_dealt_quantity = 0
            while refresh_count < max_refresh_count and not (
                    hsi_completed is True and mhi_completed is True) and is_active is True:
                time.sleep(constants.REFRESH_ORDER_STATUS_SECOND_INTERVAL)
                is_active = self.check_trade_record_is_active_by_trade_id(trade_id)
                order_list = self.trade_manager.get_order_list_by_order_id_list(order_id_list)
                for order in order_list:
                    order_code = order['code']
                    order_status = order['order_status']
                    dealt_qty = order['dealt_qty']
                    if constants.TradeProductCode.HSI in order_code:
                        order_product_code = constants.TradeProductCode.HSI
                    else:
                        order_product_code = constants.TradeProductCode.MHI
                    if order_status == ft.OrderStatus.FILLED_PART:
                        if order_product_code == constants.TradeProductCode.HSI and dealt_qty > current_hsi_dealt_quantity:
                            current_hsi_dealt_quantity = dealt_qty
                            self.log_partly_traded_order(order, trade_direction)
                        elif order_product_code == constants.TradeProductCode.MHI and dealt_qty > current_mhi_dealt_quantity:
                            current_mhi_dealt_quantity = dealt_qty
                            self.log_partly_traded_order(order, trade_direction)
                    elif is_active is False or order_status == ft.OrderStatus.FAILED or order_status == ft.OrderStatus.FILLED_ALL \
                            or order_status == ft.OrderStatus.SUBMIT_FAILED:
                        if order_product_code == constants.TradeProductCode.HSI:
                            hsi_completed = True
                        elif order_product_code == constants.TradeProductCode.MHI:
                            mhi_completed = True
                refresh_count += 1
            if refresh_count >= max_refresh_count or is_active is False:
                to_be_cancelled_order_id_list = []
                for order in order_list:
                    order_status = order['order_status']
                    if order_status == ft.OrderStatus.SUBMITTED or order_status == ft.OrderStatus.FILLED_PART:
                        to_be_cancelled_order_id_list.append(order['order_id'])
                        self.trade_manager.cancel_order(order)
                while len(to_be_cancelled_order_id_list) > 0:
                    to_be_cancelled_order_list = self.trade_manager.get_order_list_by_order_id_list(
                        to_be_cancelled_order_id_list)
                    to_be_cancelled_order_id_list = []
                    for order in to_be_cancelled_order_list:
                        order_status = order['order_status']
                        if order_status != ft.OrderStatus.CANCELLED_ALL and order_status != ft.OrderStatus.CANCELLED_PART:
                            to_be_cancelled_order_id_list.append(order['order_id'])
                    time.sleep(constants.REFRESH_ORDER_STATUS_SECOND_INTERVAL)
                order_list = self.trade_manager.get_order_list_by_order_id_list(order_id_list)

            for order in order_list:
                order_status = order['order_status']
                if order_status == ft.OrderStatus.CANCELLED_ALL:
                    if refresh_count >= max_refresh_count:
                        self.log_all_cancelled_trade_order(order_data, True)
                    else:
                        self.log_all_cancelled_trade_order(order_data, False)
                elif order_status == ft.OrderStatus.CANCELLED_PART:
                    if refresh_count >= max_refresh_count:
                        self.log_partly_cancelled_trade_order(order_data, True)
                    else:
                        self.log_partly_cancelled_trade_order(order_data, False)
                elif order_status == ft.OrderStatus.FILLED_ALL:
                    self.log_all_traded_order(order, trade_direction)
                else:
                    self.log_unexpected_order_status(order_status)

    async def place_close_position_order(self, trade_record, hsi_quantity_on_hand, mhi_quantity_on_hand):
        trade_settings = self.trade_settings
        trade_product_hsi = trade_settings['trade_product_hsi']
        trade_product_mhi = trade_settings['trade_product_mhi']
        trade_direction = trade_record['direction']
        trade_product_code_month = trade_record['trade_product_code_month']
        close_price_adjust_interval = int(trade_settings['close_price_adjust_interval'])
        price = int(trade_record['price'])

        def update_close_price_by_direction(p, direction):
            if direction == constants.TradeDirection.BUY:
                p = p + close_price_adjust_interval
            else:
                p = p - close_price_adjust_interval
            return p

        order_id_list = []
        if trade_product_hsi is True and hsi_quantity_on_hand > 0:
            result, order_data, error_message = self.trade_manager.place_order(constants.TradeProductCode.HSI,
                                                                               trade_product_code_month,
                                                                               trade_record['direction'], price,
                                                                               hsi_quantity_on_hand)
            self.log_place_order_result(result, order_data, error_message, trade_direction, price, hsi_quantity_on_hand)
            if result is True:
                order_id_list.append(order_data['order_id'])
        if trade_product_mhi is True and mhi_quantity_on_hand > 0:
            result, order_data, error_message = self.trade_manager.place_order(constants.TradeProductCode.MHI,
                                                                               trade_product_code_month,
                                                                               trade_record['direction'], price,
                                                                               mhi_quantity_on_hand)
            self.log_place_order_result(result, order_data, error_message, trade_direction, price, mhi_quantity_on_hand)
            if result is True:
                order_id_list.append(order_data['order_id'])

        if len(order_id_list) > 0:
            hsi_completed = False if hsi_quantity_on_hand > 0 else True
            mhi_completed = False if mhi_quantity_on_hand > 0 else True
            order_list = []
            while hsi_completed is False or mhi_completed is False:
                time.sleep(constants.REFRESH_ORDER_STATUS_SECOND_INTERVAL)
                order_list = self.trade_manager.get_order_list_by_order_id_list(order_id_list)
                for order in order_list:
                    order_status = order['order_status']
                    if constants.TradeProductCode.HSI in order['code']:
                        order_product_code = constants.TradeProductCode.HSI
                        quantity = hsi_quantity_on_hand
                    else:
                        order_product_code = constants.TradeProductCode.MHI
                        quantity = mhi_quantity_on_hand
                    if order_status == ft.OrderStatus.SUBMITTED or order_status == ft.OrderStatus.FILLED_PART:
                        price = update_close_price_by_direction(price, trade_direction)
                        self.trade_manager.modify_order(order['order_id'], price, quantity)
                    elif order_status == ft.OrderStatus.SUBMITTING:
                        pass
                    else:
                        if order_product_code == constants.TradeProductCode.HSI:
                            hsi_completed = True
                        elif order_product_code == constants.TradeProductCode.MHI:
                            mhi_completed = True
            for order in order_list:
                if order['order_status'] == ft.OrderStatus.FILLED_ALL:
                    self.log_all_traded_order(order, trade_direction)
                else:
                    self.log_unexpected_order_status(order_status)

    def log_place_order_result(self, result, order_data, error_message, trade_direction, price, quantity):
        if result is True:
            self.console_write_line(
                f"下單成功, 產品編號:{order_data['code']}, 方向:{constants.TRADE_DIRECTION_DESCRIPTION[trade_direction]}, "
                f"價格:{price}, 數量:{quantity}, 時間:{utils.get_hong_kong_datetime_str_in_default_format()}")
        else:
            self.console_write_line(f'下單失敗, 錯誤原因: {error_message}')

    def log_partly_traded_order(self, order_data, trade_direction):
        self.console_write_line(
            f"已完成部分交易! 產品編號:{order_data['code']}, 方向:{constants.TRADE_DIRECTION_DESCRIPTION[trade_direction]}, "
            f"成交數量:{int(order_data['dealt_qty'])}, 平均價格:{int(order_data['dealt_avg_price'])}, "
            f"時間:{utils.get_hong_kong_datetime_str_in_default_format()}")

    def log_all_traded_order(self, order_data, trade_direction):
        self.console_write_line(
            f"已完成全部交易! 產品編號:{order_data['code']}, 方向:{constants.TRADE_DIRECTION_DESCRIPTION[trade_direction]}, "
            f"成交數量:{int(order_data['dealt_qty'])}, 平均價格:{int(order_data['dealt_avg_price'])}, "
            f"時間:{utils.get_hong_kong_datetime_str_in_default_format()}")

    def log_all_cancelled_trade_order(self, order_data, is_active):
        if is_active:
            self.console_write_line(
                f"在{self.trade_settings['cancel_unfulfilled_order_after_second']}秒內未能完成產品編號:{order_data['code']}的交易, 已成功撤單!")
        else:
            self.console_write_line(f"尚未完成產品編號{order_data['code']}的交易但收到平倉訊息, 已成功撤單!")

    def log_partly_cancelled_trade_order(self, order_data, is_active):
        if is_active:
            self.console_write_line(
                f"在{self.trade_settings['cancel_unfulfilled_order_after_second']}秒內未能完成產品編號:{order_data['code']}的全部交易, 剩餘數量已成功撤單!")
        else:
            self.console_write_line(f"尚未完成產品編號{order_data['code']}的全部交易但收到平倉訊息, 剩餘數量已成功撤單!")

    def log_unexpected_order_status(self, order_status):
        self.console_write_line(f"下單發生錯誤, 訂單狀態: {order_status}")

    def get_active_trade_record_by_trade_id(self, trade_id):
        if len(self.dialog_active_trade_record_list) > 0:
            active_trade_record_list = [tr for tr in self.dialog_active_trade_record_list if
                                        tr['trade_id'] == trade_id]
            if len(active_trade_record_list) > 0:
                return active_trade_record_list[0]
        return None

    def check_trade_record_is_active_by_trade_id(self, trade_id):
        active_trade_record = self.get_active_trade_record_by_trade_id(trade_id)
        if active_trade_record is not None:
            return True
        return False

    def remove_active_trade_record_by_trade_id(self, trade_id):
        active_trade_record = self.get_active_trade_record_by_trade_id(trade_id)
        if active_trade_record is not None:
            self.dialog_active_trade_record_list.remove(active_trade_record)

    def remove_trade_record_from_dialog_trade_record_queue_list(self, trade_record):
        self.dialog_trade_record_queue_list.remove(trade_record)

    def convert_message_to_trade_record(self, text):
        hk_date = utils.get_hong_kong_datetime()
        trade_record_template_list = self.get_trade_record_template_list()
        curr_month, next_month, curr_product_code_month, next_product_code_month = get_current_next_month_and_product_code_month()

        for template in trade_record_template_list:
            template, trade_record = self.validate_dialog_message(template, text, curr_month, next_month,
                                                                  curr_product_code_month, next_product_code_month)
            if template['exist'] is True:
                if template['price_valid'] and \
                        template['time_valid'] and \
                        template['month_or_product_code_valid'] and \
                        template['has_trade_id']:
                    trade_record['description'] = template['description']
                    trade_record['action'] = template['action']
                    trade_record['direction'] = template['direction']
                    trade_time = datetime.strptime(trade_record['time'], template['time_format'])
                    trade_record['trade_time'] = trade_time
                    trade_record['formatted_time'] = trade_time.strftime(constants.DEFAULT_TIME_FORMAT)[:-3]
                    trade_record['message_received_date'] = hk_date
                    if "product_code" in trade_record:
                        trade_record['trade_product_code_month'] = trade_record['product_code'][-4:]
                    elif "month" in trade_record:
                        month = int(trade_record["month"])
                        if month == curr_month:
                            trade_record['trade_product_code_month'] = curr_product_code_month
                        elif month == next_product_code_month:
                            trade_record['trade_product_code_month'] = next_product_code_month
                    return template, trade_record
                else:
                    return template, None
        return None, None


def _run_loop(loop):
    try:
        asyncio.set_event_loop(loop)
        loop.run_forever()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


def get_current_next_month_and_product_code_month():
    hk_date = utils.get_hong_kong_datetime()
    curr_year = hk_date.year
    curr_month = hk_date.month
    next_month_year, next_month = calendar.nextmonth(year=curr_year, month=curr_month)
    curr_product_code_month = '%s%02d' % (str(curr_year)[-2:], curr_month)
    next_product_code_month = '%s%02d' % (str(next_month_year)[-2:], next_month)
    return curr_month, next_month, curr_product_code_month, next_product_code_month


if __name__ == '__main__':
    nest_asyncio.apply()
    main_loop = asyncio.get_event_loop()

    app = App(main_loop)
    _run_loop(main_loop)
