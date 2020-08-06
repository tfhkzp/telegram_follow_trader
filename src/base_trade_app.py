import tkinter as tk
from tkinter import ttk, font, messagebox
import telethon
from config import Config
from functools import partial
import threading
import logging.handlers
import sys
import constants
from styles import UI
import utils
import textwrap
import os
from sys import platform as _platform

logger = logging.getLogger('tft')

rotate_file_handler = logging.handlers.RotatingFileHandler(utils.get_dir_path_by_platform() + "tft.log",
                                                           encoding='utf-8', maxBytes=1024 * 1024 * 2,
                                                           backupCount=5)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stderr_handler = logging.StreamHandler(sys.stderr)
stdout_handler.setLevel(logging.ERROR)
handlers = [rotate_file_handler, stdout_handler, stderr_handler]
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)


class BaseTradeApp():
    app = None
    trade_app = None
    login_form = None
    config = Config()
    telegram_dialog_list = []
    async_loop = None
    tg = None

    # Disclaimer
    disclaimer_form = None

    # Login form
    login_form = None
    api_id_label = None
    api_id_var = None
    api_id_entry = None
    api_hash_label = None
    api_hash_var = None
    api_hash_entry = None
    phone_number_label = None
    phone_number_var = None
    phone_number_entry = None
    login_button = None
    verify_button_var = None

    # Verify form
    verify_phone_form = None
    verify_password_form = None

    # Trade App
    app_title = 'Telegram Follow Trader'
    # Setting
    selected_dialog_id = None
    selected_trade_mode = None

    # GUI
    setting_trade_app_frame = None
    console_trade_app_frame = None
    remark_trade_app_frame = None
    label_frame_font_style = None
    label_font_style = None
    label_width = None
    input_width = None

    # GUI - dialog
    dialog_frame = None
    dialog_select_frame = None
    dialog_select = None
    dialog_update_button = None
    dialog_button_frame = None
    dialog_test_button = None
    dialog_save_setting_button = None
    open_buy_template_var = None
    open_buy_template_entry = None
    close_buy_template_var = None
    close_buy_template_entry = None
    open_sell_template_var = None
    open_sell_template_entry = None
    close_sell_template_var = None
    close_sell_template_entry = None
    time_format_var = None
    time_format_entry = None

    # GUI - Trade Account
    trade_account_frame = None
    trade_password_entry = None
    trade_port_entry = None
    trade_port_var = None
    trade_password_test_button = None

    # GUI - Trade Setting
    trade_setting_frame = None
    trade_setting_frame_1 = None
    trade_mode_frame = None
    trade_mode_var = None
    trade_mode_fixed_quantity = None
    trade_mode_max_quantity = None
    trade_product_frame = None
    trade_product_hsi_var = None
    trade_product_mhi_var = None
    trade_product_hsi = None
    trade_product_mhi = None
    trade_quantity_frame = None
    hsi_trade_quantity_var = None
    hsi_trade_quantity_entry = None
    mhi_trade_quantity_var = None
    mhi_trade_quantity_entry = None
    hsi_margin_frame = None
    hsi_margin_var = None
    hsi_margin_entry = None
    mhi_margin_frame = None
    mhi_margin_var = None
    mhi_margin_entry = None
    trade_setting_frame_2 = None
    trade_period_frame = None
    trade_period_morning_var = None
    trade_period_afternoon_var = None
    trade_period_night_var = None
    trade_period_morning = None
    trade_period_afternoon = None
    trade_period_night = None
    open_extra_price_frame = None
    open_extra_price_var = None
    open_extra_price_entry = None
    close_price_adjust_interval_frame = None
    close_price_adjust_interval_var = None
    close_price_adjust_interval_entry = None
    cancel_unfulfilled_order_after_second_frame = None
    cancel_unfulfilled_order_after_second_var = None
    cancel_unfulfilled_order_after_second_entry = None
    trade_only_within_second_frame = None
    trade_only_within_second_var = None
    trade_only_within_second_entry = None
    trade_setting_frame_3 = None
    manual_confirm_trade_message_var = None
    manual_confirm_trade_message = None
    start_button_font_style = None
    start_follow_trade_button = None

    # GUI Console
    console_text_cache = ""
    console_text_cache_time = ""
    console_text = None
    clear_console_button = None

    # GUI Remark
    disclaimer_link = None
    github_link = None

    def __init__(self, loop):
        self.async_loop = loop
        disclaimer_version, disclaimer_content = utils.get_disclaimer_version_and_content()
        local_disclaimer_version = self.config.get_disclaimer_version()

        self.app = tk.Tk()
        if _platform != constants.MAC_PLATFORM_NAME:
            icon_file = "icon.ico"
            if not hasattr(sys, "frozen"):
                icon_file = os.path.join(os.path.dirname(__file__), icon_file)
            else:
                icon_file = os.path.join(sys.prefix, icon_file)
            if os.path.exists(icon_file):
                self.app.iconbitmap(True, icon_file)
        self.load_login_form_gui()
        self.load_login_form_config()
        self.app.lift()
        self.app.attributes('-topmost', True)
        self.app.attributes('-topmost', False)

        if disclaimer_version is not None and disclaimer_version != local_disclaimer_version:
            self.config.save_disclaimer_version(disclaimer_version)
            self.config.save_disclaimer_understand_and_agree("N")
        is_accepted = self.config.get_disclaimer_understand_and_agree()
        if is_accepted != "Y":
            self.app.withdraw()
            self.load_disclaimer(disclaimer_content)
        self.app.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.app.mainloop()

    def quit_app(self):
        pass

    def agree_disclaimer(self):
        self.config.save_disclaimer_understand_and_agree("Y")
        self.disclaimer_form.destroy()
        self.app.deiconify()
        self.app.lift()

    def load_disclaimer(self, disclaimer_content=None, read_only=False):
        if read_only is True:
            disclaimer_version, disclaimer_content = utils.get_disclaimer_version_and_content()

        def agree_checkbox_on_change():
            if agree_var1.get() is True and agree_var2.get() is True:
                self.enable_elements(confirm_button)
            else:
                self.disable_elements(confirm_button)

        disclaimer_form = tk.Toplevel(self.app)
        disclaimer_form.resizable(False, False)
        disclaimer_form.grab_set()

        disclaimer_form.lift()
        disclaimer_form.attributes('-topmost', True)
        disclaimer_form.attributes('-topmost', False)

        screenwidth = disclaimer_form.winfo_screenwidth()
        screenheight = disclaimer_form.winfo_screenheight()
        width = UI.Disclaimer.WIDTH
        height = UI.Disclaimer.HEIGHT
        if read_only is True:
            height = UI.Disclaimer.READ_ONLY_HEIGHT

        disclaimer_form.geometry('%dx%d+%d+%d' % (width, height,
                                                  (screenwidth / 2) - (width / 2), (screenheight / 2) - (height / 2)))
        disclaimer_form.title(self.app_title)
        title_font = tk.font.Font(size=UI.Disclaimer.TITLE_FONT_SIZE, underline=True, weight="bold")
        title = tk.Label(disclaimer_form, text="免責聲明", anchor=tk.W, font=title_font)
        title.pack()
        content_font = tk.font.Font(size=UI.Disclaimer.CONTENT_FONT_SIZE)

        content_frame = tk.Frame(disclaimer_form)
        canvas = tk.Canvas(content_frame, width=UI.Disclaimer.CANVAS_WIDTH,
                           height=UI.Disclaimer.CANVAS_HEIGHT)
        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox(tk.ALL)
            )
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        if disclaimer_content is not None:
            disclaimer_content_line_list = disclaimer_content.split("\n")
            for line in disclaimer_content_line_list:
                tk.Label(scrollable_frame, text=line, width=UI.Disclaimer.LABEL_WIDTH, anchor=tk.W, justify=tk.LEFT,
                         font=content_font, wraplength=UI.Disclaimer.WRAP_LENGTH, padx=UI.Disclaimer.PADDING).pack()
        else:
            tk.Label(scrollable_frame, text="無法載入內文，請參閱以下網頁的內容:", anchor=tk.W, justify=tk.LEFT,
                     font=content_font).grid(row=0, column=0, padx=UI.Disclaimer.PADDING, sticky=tk.W)
            disclaimer_link = tk.Label(scrollable_frame, text=constants.DISCLAIMER_LINK, anchor=tk.W, justify=tk.LEFT,
                                       fg="blue", cursor="hand2", font=content_font)
            disclaimer_link.grid(row=1, column=0, padx=UI.Disclaimer.PADDING, sticky=tk.W)
            disclaimer_link.bind("<Button-1>", lambda e: utils.open_link(constants.DISCLAIMER_LINK))
            tk.Label(scrollable_frame, text="所有免責聲明條款以網頁版本內文為準。", anchor=tk.W, justify=tk.LEFT,
                     font=content_font).grid(row=2, column=0, padx=UI.Disclaimer.PADDING, sticky=tk.W)
        content_frame.pack()
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        if read_only is False:
            agree_var1 = tk.BooleanVar()
            agree_checkbox1 = tk.Checkbutton(disclaimer_form, text="本人明白及同意以上聲明", anchor=tk.W, font=content_font,
                                             var=agree_var1, command=agree_checkbox_on_change)
            agree_checkbox1.pack()
            agree_checkbox1.place(x=UI.Disclaimer.AGREE_CHECKBOX1_X, y=UI.Disclaimer.AGREE_CHECKBOX1_Y)
            agree_var2 = tk.BooleanVar()
            agree_checkbox2 = tk.Checkbutton(disclaimer_form, text="本人授權該軟件收取Telegram訊息及連接證券交易服務提供者進行交易",
                                             anchor=tk.W, font=content_font, var=agree_var2,
                                             command=agree_checkbox_on_change)
            agree_checkbox2.pack()
            agree_checkbox2.place(x=UI.Disclaimer.AGREE_CHECKBOX2_X, y=UI.Disclaimer.AGREE_CHECKBOX2_Y)
            confirm_button = tk.Button(disclaimer_form, text="確定", font=content_font, command=self.agree_disclaimer,
                                       state=tk.DISABLED)
            confirm_button.pack()
            confirm_button.place(height=UI.Disclaimer.CONFIRM_BUTTON_HEIGHT, width=UI.Disclaimer.CONFIRM_BUTTON_WIDTH,
                                 x=UI.Disclaimer.CONFIRM_BUTTON_X, y=UI.Disclaimer.CONFIRM_BUTTON_Y)
            cancel_button = tk.Button(disclaimer_form, text="取消", font=content_font, command=self.quit_app)
            cancel_button.pack()
            cancel_button.place(height=UI.Disclaimer.CANCEL_BUTTON_HEIGHT, width=UI.Disclaimer.CANCEL_BUTTON_WIDTH,
                                x=UI.Disclaimer.CANCEL_BUTTON_X, y=UI.Disclaimer.CANCEL_BUTTON_Y)
            disclaimer_form.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.disclaimer_form = disclaimer_form

    def load_login_form_gui(self):
        login_form = self.app
        login_form.resizable(False, False)
        screenwidth = login_form.winfo_screenwidth()
        screenheight = login_form.winfo_screenheight()
        width = UI.LoginForm.WIDTH
        height = UI.LoginForm.HEIGHT
        login_form.geometry('%dx%d+%d+%d' % (width, height,
                                             (screenwidth / 2) - (width / 2), (screenheight / 2) - (height / 2)))
        login_form.title(self.app_title)
        label_width = UI.LoginForm.LABEL_WIDTH
        input_width = UI.LoginForm.INPUT_WIDTH
        self.api_id_label = tk.Label(login_form, text="API ID", anchor=tk.W, width=label_width)
        self.api_id_label.grid(row=0, column=0, padx=(UI.LoginForm.PADDING, 0))
        self.api_id_var = tk.StringVar()
        self.api_id_entry = tk.Entry(login_form, textvariable=self.api_id_var, width=input_width)
        self.api_id_entry.grid(row=0, column=1, padx=(0, UI.LoginForm.PADDING))
        self.api_hash_label = tk.Label(login_form, text="API Hash", anchor=tk.W, width=label_width)
        self.api_hash_label.grid(row=1, column=0, padx=(UI.LoginForm.PADDING, 0))
        self.api_hash_entry = tk.StringVar()
        self.api_hash_entry = tk.Entry(login_form, textvariable=self.api_hash_entry, width=input_width)
        self.api_hash_entry.grid(row=1, column=1, padx=(0, UI.LoginForm.PADDING))
        self.phone_number_label = tk.Label(login_form, text="電話號碼", anchor=tk.W, width=label_width)
        self.phone_number_label.grid(row=2, column=0, padx=(UI.LoginForm.PADDING, 0))
        self.phone_number_var = tk.StringVar()
        self.phone_number_entry = tk.Entry(login_form, textvariable=self.phone_number_var, width=input_width)
        self.phone_number_entry.grid(row=2, column=1, padx=(0, UI.LoginForm.PADDING))
        self.login_button = tk.Button(login_form, text="登入", command=lambda: self.run_async_task(self.login))
        self.login_button.grid(row=3, column=1, sticky=tk.E, padx=(0, UI.LoginForm.LOGIN_BUTTON_PADDING_X),
                               pady=UI.LoginForm.LOGIN_BUTTON_PADDING_Y)
        self.app = login_form

    def load_login_form_config(self):
        if constants.SAVE_TELEGRAM_LOGIN_INFORMATION:
            api_id = self.config.get_telegram_setting("api_id")
            api_hash = self.config.get_telegram_setting("api_hash")
            phone_number = self.config.get_telegram_setting("phone_number")
            if api_id is not None and api_id != "":
                self.api_id_entry.insert(tk.END, api_id)
            if api_hash is not None and api_hash != "":
                self.api_hash_entry.insert(tk.END, api_hash)
            if phone_number is not None and phone_number != "":
                self.phone_number_entry.insert(tk.END, phone_number)

    async def login(self):
        pass

    async def get_verification_code(self):
        pass

    def remove_login_form_gui(self):
        self.api_id_label.grid_remove()
        self.api_id_entry.grid_remove()
        self.api_hash_label.grid_remove()
        self.api_hash_entry.grid_remove()
        self.phone_number_label.grid_remove()
        self.phone_number_entry.grid_remove()
        self.login_button.grid_remove()

    def load_trade_app_gui(self):
        trade_app = self.app
        trade_app.title(self.app_title)
        self.remove_login_form_gui()
        screenwidth = trade_app.winfo_screenwidth()
        screenheight = trade_app.winfo_screenheight()
        width = UI.Main.WIDTH
        height = UI.Main.HEIGHT
        padding = UI.Main.PADDING
        frame_padding_x = UI.Main.FRAME_PADDING_X
        frame_padding_y = UI.Main.FRAME_PADDING_Y
        frame_width = width - (frame_padding_x * 2)
        trade_app.geometry('%dx%d+%d+%d' % (width, height,
                                            (screenwidth / 2) - (width / 2),
                                            (screenheight / 2) - (height / 2)))
        trade_app.resizable(False, False)

        self.label_frame_font_style = tk.font.Font(size=UI.Main.FRAME_FONT_SIZE)
        self.label_font_style = tk.font.Font(size=UI.Main.CONTENT_FONT_SIZE)
        self.label_width = UI.Main.LABEL_WIDTH
        self.input_width = UI.Main.INPUT_WIDTH

        self.setting_trade_app_frame = tk.Frame(trade_app, width=width, height=UI.Main.SETTING_FRAME_HEIGHT)
        self.console_trade_app_frame = tk.Frame(trade_app, width=width, height=UI.Main.CONSOLE_FRAME_HEIGHT)
        self.remark_trade_app_frame = tk.Frame(trade_app, width=width, bg="yellow", height=UI.Main.REMARK_FRAME_HEIGHT)

        self.dialog_frame = tk.LabelFrame(self.setting_trade_app_frame, text='頻道設定', font=self.label_frame_font_style,
                                          width=frame_width,
                                          height=UI.Main.DIALOG_FRAME_HEIGHT, padx=frame_padding_x,
                                          pady=frame_padding_y)
        self.dialog_frame.grid_propagate(False)
        self.dialog_frame.grid(row=0, padx=frame_padding_x, pady=frame_padding_y)
        tk.Label(self.dialog_frame, text="選擇頻道", font=self.label_font_style, width=self.label_width, anchor=tk.W) \
            .grid(row=0, column=0, padx=0, pady=(padding, 0), sticky=tk.W)
        self.dialog_select_frame = tk.Frame(self.dialog_frame)
        self.dialog_select_frame.grid(row=0, column=1, columnspan=4, sticky=tk.W)
        self.dialog_select = ttk.Combobox(self.dialog_select_frame, state="readonly", width=UI.Main.DIALOG_SELECT_WIDTH)
        self.dialog_select.grid(row=0, column=0, sticky=tk.W, pady=padding)
        self.dialog_select.bind("<<ComboboxSelected>>", self.dialog_select_on_select)
        self.dialog_update_button = tk.Button(self.dialog_select_frame, text="刷新", font=self.label_font_style,
                                              command=lambda: self.run_async_task(self.refresh_dialog_list))
        self.dialog_update_button.grid(row=0, column=1, sticky=tk.W, padx=padding, pady=padding)
        self.dialog_test_button = tk.Button(self.dialog_select_frame, text="測試", font=self.label_font_style,
                                            command=lambda: self.run_async_task(self.test_dialog_setting),
                                            state=tk.DISABLED)
        self.dialog_test_button.grid(row=0, column=2, sticky=tk.NE, padx=(0, padding), pady=padding)
        self.dialog_save_setting_button = tk.Button(self.dialog_select_frame, text="儲存訊息設定",
                                                    font=self.label_font_style,
                                                    command=self.save_dialog_setting, state=tk.DISABLED)
        self.dialog_save_setting_button.grid(row=0, column=3, sticky=tk.NE,
                                             padx=(0, UI.Main.DIALOG_SAVE_SETTING_BUTTON_PADDING_X),
                                             pady=UI.Main.DIALOG_SAVE_SETTING_BUTTON_PADDING_Y)
        tk.Label(self.dialog_frame, text="建好倉訊息", font=self.label_font_style, width=self.label_width,
                 anchor=tk.W) \
            .grid(row=1, column=0, padx=0, pady=(0, padding), sticky=tk.W)
        self.open_buy_template_var = tk.StringVar()
        self.open_buy_template_entry = tk.Entry(self.dialog_frame, textvariable=self.open_buy_template_var,
                                                width=self.input_width,
                                                state=tk.DISABLED)
        self.open_buy_template_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, UI.Main.DIALOG_INPUT_PADDING_X),
                                          pady=(0, padding))
        tk.Label(self.dialog_frame, text="平好倉訊息", font=self.label_font_style, width=self.label_width, anchor=tk.W) \
            .grid(row=1, column=2, padx=0, pady=(0, padding), sticky=tk.W)
        self.close_buy_template_var = tk.StringVar()
        self.close_buy_template_entry = tk.Entry(self.dialog_frame, textvariable=self.close_buy_template_var,
                                                 width=self.input_width,
                                                 state=tk.DISABLED)
        self.close_buy_template_entry.grid(row=1, column=3, sticky=tk.W, padx=(0, UI.Main.DIALOG_INPUT_RIGHT_PADDING_X),
                                           pady=(0, padding))

        tk.Label(self.dialog_frame, text="建淡倉訊息", font=self.label_font_style, width=self.label_width, anchor=tk.W) \
            .grid(row=2, column=0, padx=0, pady=(0, padding), sticky=tk.W)
        self.open_sell_template_var = tk.StringVar()
        self.open_sell_template_entry = tk.Entry(self.dialog_frame, textvariable=self.open_sell_template_var,
                                                 width=self.input_width,
                                                 state=tk.DISABLED)
        self.open_sell_template_entry.grid(row=2, column=1, sticky=tk.W, padx=(0, UI.Main.DIALOG_INPUT_PADDING_X),
                                           pady=(0, padding))
        tk.Label(self.dialog_frame, text="平淡倉訊息", font=self.label_font_style, width=self.label_width, anchor=tk.W) \
            .grid(row=2, column=2, padx=0, pady=(0, padding))
        self.close_sell_template_var = tk.StringVar()
        self.close_sell_template_entry = tk.Entry(self.dialog_frame, textvariable=self.close_sell_template_var,
                                                  width=self.input_width,
                                                  state=tk.DISABLED)
        self.close_sell_template_entry.grid(row=2, column=3, sticky=tk.W,
                                            padx=(0, UI.Main.DIALOG_INPUT_RIGHT_PADDING_X),
                                            pady=(0, padding))

        tk.Label(self.dialog_frame, text="時間格式", font=self.label_font_style, width=self.label_width, anchor=tk.W) \
            .grid(row=3, column=0, padx=0, pady=(0, padding), sticky=tk.W)
        self.time_format_var = tk.StringVar()
        self.time_format_entry = tk.Entry(self.dialog_frame, textvariable=self.time_format_var, width=self.input_width,
                                          state=tk.DISABLED)
        self.time_format_entry.grid(row=3, column=1, sticky=tk.W, padx=(0, UI.Main.DIALOG_INPUT_PADDING_X),
                                    pady=UI.Main.TIME_FORMAT_INPUT_PADDING_Y)

        self.trade_account_frame = tk.LabelFrame(self.setting_trade_app_frame, text='交易帳戶',
                                                 font=self.label_frame_font_style,
                                                 width=frame_width,
                                                 height=UI.Main.TRADE_ACCOUNT_FRAME_HEIGHT,
                                                 padx=frame_padding_x, pady=frame_padding_y)
        self.trade_account_frame.grid_propagate(False)
        self.trade_account_frame.grid(row=1, padx=frame_padding_x, pady=0)
        tk.Label(self.trade_account_frame, text="交易密碼", font=self.label_font_style,
                 width=UI.Main.TRADE_PASSWORD_LABEL_WIDTH, anchor=tk.W) \
            .grid(row=0, column=0, padx=0, pady=(0, 0), sticky=tk.W)

        self.trade_password_entry = tk.Entry(self.trade_account_frame, textvariable=tk.StringVar(),
                                             width=UI.Main.TRADE_PASSWORD_INPUT_WIDTH, show="*")
        self.trade_password_entry.grid(row=0, column=1, padx=UI.Main.TRADE_PASSWORD_INPUT_PADDING_X, pady=0,
                                       sticky=tk.W)

        tk.Label(self.trade_account_frame, text="端口(0-65535)", font=self.label_font_style,
                 width=UI.Main.TRADE_PORT_INPUT_WIDTH, anchor=tk.E) \
            .grid(row=0, column=2, padx=(padding, 0), pady=0)

        self.trade_port_var = tk.StringVar()
        self.trade_port_var.trace(tk.W,
                                  lambda name, index, mode, sv=self.trade_port_var: self.trade_port_entry_on_change(sv))
        self.trade_port_entry = tk.Entry(self.trade_account_frame, textvariable=self.trade_port_var, width=6)
        self.trade_port_entry.grid(row=0, column=3, padx=UI.Main.TRADE_PORT_INPUT_PADDING_X,
                                   pady=0)

        self.trade_password_test_button = tk.Button(self.trade_account_frame, text="測試", font=self.label_font_style,
                                                    command=lambda: self.run_async_task(
                                                        self.test_trade_account_setting))
        self.trade_password_test_button.grid(row=0, column=4, sticky=tk.NE,
                                             padx=(0, UI.Main.TRADE_PASSWORD_TEST_BUTTON_PADDING_X),
                                             pady=UI.Main.TRADE_PASSWORD_TEST_BUTTON_PADDING_Y)

        trade_setting_frame_height = UI.Main.TRADE_SETTING_FRAME_HEIGHT
        self.trade_setting_frame = tk.LabelFrame(self.setting_trade_app_frame, text='交易設定',
                                                 font=self.label_frame_font_style,
                                                 width=frame_width,
                                                 height=trade_setting_frame_height)
        self.trade_setting_frame.grid_propagate(False)
        self.trade_setting_frame.grid(row=2, padx=frame_padding_x, pady=frame_padding_y)

        self.trade_setting_frame_1 = tk.Frame(self.trade_setting_frame, width=UI.Main.TRADE_SETTING_FRAME_1_WIDTH,
                                              height=trade_setting_frame_height - 20, padx=frame_padding_x,
                                              pady=frame_padding_y)
        self.trade_setting_frame_1.grid(row=0, column=0, sticky=tk.N)
        self.trade_setting_frame_1.grid_propagate(False)
        self.trade_mode_frame = tk.Frame(self.trade_setting_frame_1)
        self.trade_mode_frame.grid(row=0, column=0, sticky=tk.W)
        tk.Label(self.trade_mode_frame, text="交易模式", font=self.label_font_style, width=UI.Main.TRADE_MODE_LABEL_WIDTH,
                 anchor=tk.W) \
            .grid(row=0, column=0, padx=0, pady=UI.Main.TRADE_MODE_LABEL_PADDING_Y, sticky=tk.W)
        self.trade_mode_var = tk.StringVar()
        self.trade_mode_var.set(constants.TradeMode.FIXED_QUANTITY)
        self.trade_mode_fixed_quantity = tk.Radiobutton(self.trade_mode_frame, text="固定數量", font=self.label_font_style,
                                                        variable=self.trade_mode_var,
                                                        value=constants.TradeMode.FIXED_QUANTITY,
                                                        command=self.trade_mode_checkbox_on_change)
        self.trade_mode_max_quantity = tk.Radiobutton(self.trade_mode_frame, text="自動檢測最大可買數量",
                                                      font=self.label_font_style,
                                                      variable=self.trade_mode_var,
                                                      value=constants.TradeMode.MAX_QUANTITY,
                                                      command=self.trade_mode_checkbox_on_change)
        self.trade_mode_fixed_quantity.grid(row=0, column=1, pady=UI.Main.TRADE_MODE_CHECKBOX_PADDING_Y, sticky=tk.W)
        self.trade_mode_max_quantity.grid(row=0, column=2, pady=UI.Main.TRADE_MODE_CHECKBOX_PADDING_Y, sticky=tk.W)

        self.trade_product_frame = tk.Frame(self.trade_setting_frame_1)
        self.trade_product_frame.grid(row=1, column=0, sticky=tk.W)
        tk.Label(self.trade_product_frame, text="交易產品", font=self.label_font_style,
                 width=UI.Main.TRADE_PRODUCT_LABEL_WIDTH, anchor=tk.W) \
            .grid(row=0, column=0, padx=UI.Main.TRADE_PRODUCT_LABEL_PADDING_X,
                  pady=UI.Main.TRADE_PRODUCT_LABEL_PADDING_Y, sticky=tk.W)
        self.trade_product_hsi_var = tk.BooleanVar()
        self.trade_product_mhi_var = tk.BooleanVar()

        self.trade_product_hsi = tk.Checkbutton(self.trade_product_frame, text="恆生指數期貨", font=self.label_font_style,
                                                var=self.trade_product_hsi_var,
                                                command=self.trade_product_checkbox_on_change)
        self.trade_product_mhi = tk.Checkbutton(self.trade_product_frame, text="小型恆生指數期貨", font=self.label_font_style,
                                                var=self.trade_product_mhi_var,
                                                command=self.trade_product_checkbox_on_change)
        self.trade_product_hsi.grid(row=0, column=1, pady=UI.Main.TRADE_PRODUCT_CHECKBOX_PADDING_Y, sticky=tk.W)
        self.trade_product_mhi.grid(row=0, column=2, pady=UI.Main.TRADE_PRODUCT_CHECKBOX_PADDING_Y, sticky=tk.W)

        self.trade_quantity_frame = tk.Frame(self.trade_setting_frame_1)
        self.trade_quantity_frame.grid(row=2, column=0, sticky=tk.W)
        tk.Label(self.trade_quantity_frame, text="期貨交易數量", font=self.label_font_style,
                 width=UI.Main.HSI_TRADE_QUANTITY_LABEL_WIDTH, anchor=tk.W) \
            .grid(row=0, column=0, padx=UI.Main.TRADE_QUANTITY_LABEL_PADDING_X,
                  pady=UI.Main.TRADE_QUANTITY_LABEL_PADDING_Y, sticky=tk.W)
        self.hsi_trade_quantity_var = tk.StringVar()
        self.hsi_trade_quantity_var.trace(tk.W,
                                          lambda name, index, mode,
                                                 sv=self.hsi_trade_quantity_var:
                                          self.trade_setting_entry_on_change(sv, "hsi_trade_quantity",
                                                                             constants.TkinterEntryType.POSITIVE_INTEGER))
        self.hsi_trade_quantity_entry = tk.Entry(self.trade_quantity_frame, textvariable=self.hsi_trade_quantity_var,
                                                 width=UI.Main.TRADE_QUANTITY_INPUT_WIDTH,
                                                 justify='center')
        self.hsi_trade_quantity_entry.bind('<Control-v>', lambda e: 'break')
        self.hsi_trade_quantity_entry.grid(row=0, column=1, padx=UI.Main.TRADE_QUANTITY_INPUT_PADDING_X,
                                           pady=UI.Main.TRADE_QUANTITY_LABEL_PADDING_Y)

        tk.Label(self.trade_quantity_frame, text="小型期貨交易數量", font=self.label_font_style,
                 width=UI.Main.MHI_TRADE_QUANTITY_LABEL_WIDTH, anchor=tk.W) \
            .grid(row=0, column=2, padx=UI.Main.TRADE_QUANTITY_LABEL_PADDING_X,
                  pady=UI.Main.TRADE_QUANTITY_LABEL_PADDING_Y)
        self.mhi_trade_quantity_var = tk.StringVar()
        self.mhi_trade_quantity_var.trace(tk.W,
                                          lambda name, index, mode,
                                                 sv=self.mhi_trade_quantity_var:
                                          self.trade_setting_entry_on_change(sv, "mhi_trade_quantity",
                                                                             constants.TkinterEntryType.POSITIVE_INTEGER))
        self.mhi_trade_quantity_entry = tk.Entry(self.trade_quantity_frame, textvariable=self.mhi_trade_quantity_var,
                                                 width=UI.Main.TRADE_QUANTITY_INPUT_WIDTH,
                                                 justify='center')
        self.mhi_trade_quantity_entry.bind('<Control-v>', lambda e: 'break')
        self.mhi_trade_quantity_entry.grid(row=0, column=3, padx=UI.Main.TRADE_QUANTITY_INPUT_PADDING_X,
                                           pady=UI.Main.TRADE_QUANTITY_INPUT_PADDING_Y)

        self.hsi_margin_frame = tk.Frame(self.trade_setting_frame_1)
        self.hsi_margin_frame.grid(row=3, column=0, sticky=tk.W)
        tk.Label(self.hsi_margin_frame, text="每達保證金", font=self.label_font_style, width=UI.Main.MARGIN_LABEL_WIDTH,
                 anchor=tk.W) \
            .grid(row=3, column=0, padx=UI.Main.MARGIN_LABEL_PADDING_X, pady=UI.Main.MARGIN_LABEL_PADDING_Y,
                  sticky=tk.W)
        self.hsi_margin_var = tk.StringVar()
        self.hsi_margin_var.trace(tk.W,
                                  lambda name, index, mode,
                                         sv=self.hsi_margin_var:
                                  self.trade_setting_entry_on_change(sv, "hsi_margin",
                                                                     constants.TkinterEntryType.POSITIVE_INTEGER))
        self.hsi_margin_entry = tk.Entry(self.hsi_margin_frame, textvariable=self.hsi_margin_var,
                                         width=UI.Main.MARGIN_INPUT_WIDTH,
                                         justify='center')
        self.hsi_margin_entry.bind('<Control-v>', lambda e: 'break')
        self.hsi_margin_entry.grid(row=3, column=1, padx=UI.Main.MARGIN_INPUT_PADDING_X,
                                   pady=UI.Main.MARGIN_INPUT_PADDING_Y)
        tk.Label(self.hsi_margin_frame, text="交易期貨一張", font=self.label_font_style, width=UI.Main.HSI_MARGIN_LABEL_WIDTH,
                 anchor=tk.W) \
            .grid(row=3, column=2, padx=(0, 0), pady=UI.Main.MARGIN_LABEL_PADDING_Y)

        self.mhi_margin_frame = tk.Frame(self.trade_setting_frame_1)
        self.mhi_margin_frame.grid(row=4, column=0, sticky=tk.W)
        tk.Label(self.mhi_margin_frame, text="每達保證金", font=self.label_font_style, width=UI.Main.MARGIN_LABEL_WIDTH,
                 anchor=tk.W) \
            .grid(row=3, column=0, padx=UI.Main.MARGIN_LABEL_PADDING_X, pady=UI.Main.MARGIN_LABEL_PADDING_Y)
        self.mhi_margin_var = tk.StringVar()
        self.mhi_margin_var.trace(tk.W,
                                  lambda name, index, mode,
                                         sv=self.mhi_margin_var:
                                  self.trade_setting_entry_on_change(sv, "mhi_margin",
                                                                     constants.TkinterEntryType.POSITIVE_INTEGER))
        self.mhi_margin_entry = tk.Entry(self.mhi_margin_frame, textvariable=self.mhi_margin_var,
                                         width=UI.Main.MARGIN_INPUT_WIDTH,
                                         justify='center')
        self.mhi_margin_entry.bind('<Control-v>', lambda e: 'break')
        self.mhi_margin_entry.grid(row=3, column=1, padx=UI.Main.MARGIN_INPUT_PADDING_X,
                                   pady=UI.Main.MARGIN_INPUT_PADDING_Y)
        tk.Label(self.mhi_margin_frame, text="交易小型期貨一張", font=self.label_font_style,
                 width=UI.Main.MHI_MARGIN_LABEL_WIDTH, anchor=tk.W) \
            .grid(row=3, column=2, padx=(0, 0), pady=UI.Main.MARGIN_LABEL_PADDING_Y)

        self.trade_setting_frame_2 = tk.Frame(self.trade_setting_frame, width=UI.Main.TRADE_SETTING_FRAME_2_WIDTH,
                                              height=trade_setting_frame_height - 20,
                                              padx=frame_padding_x, pady=frame_padding_y)
        self.trade_setting_frame_2.grid(row=0, column=1, sticky=tk.N)
        self.trade_setting_frame_2.grid_propagate(False)
        self.trade_period_frame = tk.Frame(self.trade_setting_frame_2)
        self.trade_period_frame.grid(row=0, column=0, sticky=tk.NW)
        tk.Label(self.trade_period_frame, text="交易時段", font=self.label_font_style,
                 width=UI.Main.TRADE_PERIOD_LABEL_WIDTH, anchor=tk.W) \
            .grid(row=0, column=0, padx=UI.Main.TRADE_PERIOD_LABEL_PADDING_X, pady=UI.Main.TRADE_PERIOD_LABEL_PADDING_Y)
        self.trade_period_morning_var = tk.BooleanVar()
        self.trade_period_afternoon_var = tk.BooleanVar()
        self.trade_period_night_var = tk.BooleanVar()
        self.trade_period_morning = tk.Checkbutton(self.trade_period_frame, text="上午", font=self.label_font_style,
                                                   var=self.trade_period_morning_var,
                                                   command=partial(self.trade_setting_checkbox_on_change,
                                                                   self.trade_period_morning_var,
                                                                   "trade_period_morning"))
        self.trade_period_afternoon = tk.Checkbutton(self.trade_period_frame, text="下午", font=self.label_font_style,
                                                     var=self.trade_period_afternoon_var,
                                                     command=partial(self.trade_setting_checkbox_on_change,
                                                                     self.trade_period_afternoon_var,
                                                                     "trade_period_afternoon"))
        self.trade_period_night = tk.Checkbutton(self.trade_period_frame, text="晚上", font=self.label_font_style,
                                                 var=self.trade_period_night_var,
                                                 command=partial(self.trade_setting_checkbox_on_change,
                                                                 self.trade_period_night_var,
                                                                 "trade_period_night"))
        self.trade_period_morning.grid(row=0, column=1, pady=UI.Main.TRADE_PERIOD_CHECKBOX_PADDING_Y, sticky=tk.W)
        self.trade_period_afternoon.grid(row=0, column=2, pady=UI.Main.TRADE_PERIOD_CHECKBOX_PADDING_Y, sticky=tk.W)
        self.trade_period_night.grid(row=0, column=3, pady=UI.Main.TRADE_PERIOD_CHECKBOX_PADDING_Y, sticky=tk.W)

        self.open_extra_price_frame = tk.Frame(self.trade_setting_frame_2)
        self.open_extra_price_frame.grid(row=1, column=0, sticky=tk.W)

        tk.Label(self.open_extra_price_frame, text="建倉追價", font=self.label_font_style,
                 width=UI.Main.OPEN_EXTRA_PRICE_LABEL_WIDTH, anchor=tk.W) \
            .grid(row=0, column=0, padx=UI.Main.OPEN_EXTRA_PRICE_LABEL_PADDING_X,
                  pady=UI.Main.OPEN_EXTRA_PRICE_LABEL_PADDING_Y)
        self.open_extra_price_var = tk.StringVar()
        self.open_extra_price_var.trace(tk.W,
                                        lambda name, index, mode,
                                               sv=self.open_extra_price_var:
                                        self.trade_setting_entry_on_change(sv, "open_extra_price",
                                                                           constants.TkinterEntryType.INTEGER))
        self.open_extra_price_entry = tk.Entry(self.open_extra_price_frame, textvariable=self.open_extra_price_var,
                                               width=UI.Main.OPEN_EXTRA_PRICE_INPUT_WIDTH,
                                               justify='center')
        self.open_extra_price_entry.bind('<Control-v>', lambda e: 'break')
        self.open_extra_price_entry.grid(row=0, column=1, padx=UI.Main.OPEN_EXTRA_PRICE_INPUT_PADDING_X,
                                         pady=UI.Main.OPEN_EXTRA_PRICE_INPUT_PADDING_Y)

        self.close_price_adjust_interval_frame = tk.Frame(self.trade_setting_frame_2)
        self.close_price_adjust_interval_frame.grid(row=2, column=0, sticky=tk.W)
        tk.Label(self.close_price_adjust_interval_frame, text="平倉調整價格區間", font=self.label_font_style,
                 width=UI.Main.CLOSE_PRICE_ADJUST_INTERVAL_LABEL_WIDTH,
                 anchor=tk.W) \
            .grid(row=0, column=0, padx=UI.Main.CLOSE_PRICE_ADJUST_INTERVAL_LABEL_PADDING_X,
                  pady=UI.Main.CLOSE_PRICE_ADJUST_INTERVAL_LABEL_PADDING_Y)
        self.close_price_adjust_interval_var = tk.StringVar()
        self.close_price_adjust_interval_var.trace(tk.W,
                                                   lambda name, index, mode,
                                                          sv=self.close_price_adjust_interval_var:
                                                   self.trade_setting_entry_on_change(sv, "close_price_adjust_interval",
                                                                                      constants.TkinterEntryType.POSITIVE_INTEGER))
        self.close_price_adjust_interval_entry = tk.Entry(self.close_price_adjust_interval_frame,
                                                          textvariable=self.close_price_adjust_interval_var,
                                                          width=UI.Main.CLOSE_PRICE_ADJUST_INTERVAL_INPUT_WIDTH,
                                                          justify='center')
        self.close_price_adjust_interval_entry.bind('<Control-v>', lambda e: 'break')
        self.close_price_adjust_interval_entry.grid(row=0, column=1,
                                                    padx=UI.Main.CLOSE_PRICE_ADJUST_INTERVAL_INPUT_PADDING_X,
                                                    pady=UI.Main.CLOSE_PRICE_ADJUST_INTERVAL_INPUT_PADDING_Y)
        self.cancel_unfulfilled_order_after_second_frame = tk.Frame(self.trade_setting_frame_2)
        self.cancel_unfulfilled_order_after_second_frame.grid(row=3, column=0, sticky=tk.W)
        tk.Label(self.cancel_unfulfilled_order_after_second_frame, text="等待", font=self.label_font_style,
                 width=UI.Main.CANCEL_UNFULFILLED_ORDER_AFTER_SECOND_LABEL_1_WIDTH, anchor=tk.W) \
            .grid(row=0, column=0, padx=UI.Main.CANCEL_UNFULFILLED_ORDER_AFTER_SECOND_LABEL_PADDING_X,
                  pady=UI.Main.CANCEL_UNFULFILLED_ORDER_AFTER_SECOND_LABEL_PADDING_Y)
        self.cancel_unfulfilled_order_after_second_var = tk.StringVar()
        self.cancel_unfulfilled_order_after_second_var.trace(tk.W,
                                                             lambda name, index, mode,
                                                                    sv=self.cancel_unfulfilled_order_after_second_var:
                                                             self.trade_setting_entry_on_change(sv,
                                                                                                "cancel_unfulfilled_order_after_second",
                                                                                                constants.TkinterEntryType.FLOAT))
        self.cancel_unfulfilled_order_after_second_entry = \
            tk.Entry(self.cancel_unfulfilled_order_after_second_frame,
                     textvariable=self.cancel_unfulfilled_order_after_second_var,
                     width=UI.Main.CANCEL_UNFULFILLED_ORDER_AFTER_SECOND_INPUT_WIDTH,
                     justify='center')
        self.cancel_unfulfilled_order_after_second_entry \
            .grid(row=0, column=1, padx=UI.Main.CANCEL_UNFULFILLED_ORDER_AFTER_SECOND_INPUT_PADDING_X,
                  pady=UI.Main.CANCEL_UNFULFILLED_ORDER_AFTER_SECOND_INPUT_PADDING_Y, sticky=tk.E)
        self.cancel_unfulfilled_order_after_second_entry.bind('<Control-v>', lambda e: 'break')
        tk.Label(self.cancel_unfulfilled_order_after_second_frame, text="秒後取消未成交的建倉訂單", font=self.label_font_style,
                 width=UI.Main.CANCEL_UNFULFILLED_ORDER_AFTER_SECOND_LABEL_2_WIDTH,
                 anchor=tk.W) \
            .grid(row=0, column=2, padx=UI.Main.CANCEL_UNFULFILLED_ORDER_AFTER_SECOND_LABEL_PADDING_X
                  , pady=UI.Main.CANCEL_UNFULFILLED_ORDER_AFTER_SECOND_LABEL_PADDING_Y)

        self.trade_only_within_second_frame = tk.Frame(self.trade_setting_frame_2)
        self.trade_only_within_second_frame.grid(row=4, column=0, sticky=tk.W)
        tk.Label(self.trade_only_within_second_frame, text="忽略延誤", font=self.label_font_style,
                 width=UI.Main.TRADE_ONLY_WITHIN_SECOND_LABEL_1_WIDTH, anchor=tk.W) \
            .grid(row=0, column=0, padx=UI.Main.TRADE_ONLY_WITHIN_SECOND_LABEL_PADDING_X,
                  pady=UI.Main.TRADE_ONLY_WITHIN_SECOND_LABEL_PADDING_Y)

        self.trade_only_within_second_var = tk.StringVar()
        self.trade_only_within_second_var.trace(tk.W,
                                                lambda name, index, mode,
                                                       sv=self.trade_only_within_second_var:
                                                self.trade_setting_entry_on_change(sv,
                                                                                   "trade_only_within_second",
                                                                                   constants.TkinterEntryType.FLOAT))

        self.trade_only_within_second_entry = tk.Entry(self.trade_only_within_second_frame,
                                                       textvariable=self.trade_only_within_second_var,
                                                       width=UI.Main.TRADE_ONLY_WITHIN_SECOND_INPUT_WIDTH,
                                                       justify='center')
        self.trade_only_within_second_entry.bind('<Control-v>', lambda e: 'break')
        self.trade_only_within_second_entry.grid(row=0, column=1, padx=UI.Main.TRADE_ONLY_WITHIN_SECOND_INPUT_PADDING_X,
                                                 pady=UI.Main.TRADE_ONLY_WITHIN_SECOND_INPUT_PADDING_Y, sticky=tk.E)
        tk.Label(self.trade_only_within_second_frame, text="秒以上的交易訊息", font=self.label_font_style,
                 width=UI.Main.TRADE_ONLY_WITHIN_SECOND_LABEL_2_WIDTH,
                 anchor=tk.W) \
            .grid(row=0, column=2, padx=UI.Main.TRADE_ONLY_WITHIN_SECOND_LABEL_PADDING_X,
                  pady=UI.Main.TRADE_ONLY_WITHIN_SECOND_LABEL_PADDING_Y)

        self.trade_setting_frame_3 = tk.Frame(self.trade_setting_frame, width=UI.Main.TRADE_SETTING_FRAME_3_WIDTH,
                                              height=trade_setting_frame_height - 20,
                                              padx=0, pady=frame_padding_y)
        self.trade_setting_frame_3.grid(row=0, column=2, sticky=tk.NE)
        self.trade_setting_frame_3.grid_propagate(False)
        self.trade_setting_frame_3.grid_rowconfigure(0, weight=1)
        self.trade_setting_frame_3.grid_columnconfigure(0, weight=1)

        self.manual_confirm_trade_message_var = tk.BooleanVar()
        self.manual_confirm_trade_message = tk.Checkbutton(self.trade_setting_frame_3, text="手動確認每筆交易",
                                                           font=self.label_font_style,
                                                           var=self.manual_confirm_trade_message_var,
                                                           command=partial(self.trade_setting_checkbox_on_change,
                                                                           self.manual_confirm_trade_message_var,
                                                                           "manual_confirm_trade_message"))
        self.manual_confirm_trade_message.grid(row=0, column=0,
                                               pady=UI.Main.MANUAL_CONFIRM_TRADE_MESSAGE_CHECKBOX_PADDING_Y,
                                               sticky=tk.NE)

        self.start_button_font_style = tk.font.Font(size=UI.Main.START_BUTTON_FONT_SIZE)
        self.start_follow_trade_button = tk.Button(self.trade_setting_frame_3, text="開始",
                                                   font=self.start_button_font_style,
                                                   command=lambda: self.run_async_task(self.start_follow_trade))
        self.start_follow_trade_button.grid(row=1, column=0, sticky=tk.NE, padx=UI.Main.START_BUTTON_PADDING_X,
                                            pady=UI.Main.START_BUTTON_PADDING_Y)

        self.setting_trade_app_frame.grid(row=0)
        self.console_trade_app_frame.grid(row=1)
        self.remark_trade_app_frame.grid(row=2, sticky=tk.E, padx=frame_padding_x)
        scrollbar = tk.Scrollbar(self.console_trade_app_frame)
        console_text_font = tk.font.Font(size=UI.Main.CONSOLE_TEXT_FONT_SIZE)
        console_text_font_bold = tk.font.Font(size=UI.Main.CONSOLE_TEXT_FONT_SIZE, name="bold")
        console_text_font_bold.configure(weight="bold")

        self.console_text = tk.Text(self.console_trade_app_frame, width=UI.Main.CONSOLE_TEXT_WIDTH,
                                    height=UI.Main.CONSOLE_TEXT_HEIGHT,
                                    wrap="word", bg=constants.Color.DARK, fg=constants.Color.TEXT,
                                    yscrollcommand=scrollbar.set,
                                    borderwidth=0, highlightthickness=0,
                                    font=console_text_font,
                                    selectbackground=constants.Color.CONSTRAST,
                                    state=tk.DISABLED)
        scrollbar.config(command=self.console_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.console_text.tag_config(constants.TkinterTextColorTag.LogTime.TITLE,
                                     foreground=constants.TkinterTextColorTag.LogTime.FG_COLOR)
        self.console_text.tag_config(constants.TkinterTextColorTag.Success.TITLE,
                                     background=constants.TkinterTextColorTag.Success.BG_COLOR)
        self.console_text.tag_config(constants.TkinterTextColorTag.Warning.TITLE,
                                     background=constants.TkinterTextColorTag.Warning.BG_COLOR)
        self.console_text.tag_config(constants.TkinterTextColorTag.Error.TITLE,
                                     background=constants.TkinterTextColorTag.Error.BG_COLOR)
        self.console_text.tag_config(constants.TkinterTextColorTag.Info.TITLE,
                                     background=constants.TkinterTextColorTag.Info.BG_COLOR)
        self.console_text.tag_config(constants.TkinterTextColorTag.Sharp.TITLE,
                                     foreground=constants.TkinterTextColorTag.Sharp.FG_COLOR)

        self.console_trade_app_frame.grid(row=1)
        self.clear_console_button = tk.Button(self.console_trade_app_frame, text="清除",
                                              font=self.label_font_style,
                                              command=self.clear_console)
        self.clear_console_button.place(x=UI.Main.CLEAR_CONSOLE_BUTTON_X, y=UI.Main.CLEAR_CONSOLE_BUTTON_Y)

        self.disclaimer_link = tk.Label(self.remark_trade_app_frame, text="免責聲明", fg="blue", cursor="hand2")
        self.disclaimer_link.grid(row=0, column=0, sticky=tk.E)
        self.disclaimer_link.bind("<Button-1>", lambda e: self.load_disclaimer(read_only=True))
        self.github_link = tk.Label(self.remark_trade_app_frame, text="GitHub", fg="blue", cursor="hand2")
        self.github_link.grid(row=0, column=1, sticky=tk.E)
        self.github_link.bind("<Button-1>",
                              lambda e: utils.open_link(constants.GITHUB_REPO_LINK))
        self.app = trade_app

    def load_trade_app_config(self):
        default_telegram_dialog_id = self.config.get_default_telegram_dialog_id()
        trade_port = self.config.get_trade_port()

        if default_telegram_dialog_id is not None and default_telegram_dialog_id != "":
            default_telegram_dialog_id = int(default_telegram_dialog_id)
            telegram_dialog_id_list = [dialog['id'] for dialog in self.telegram_dialog_list]
            if default_telegram_dialog_id in telegram_dialog_id_list:
                dialog_index = telegram_dialog_id_list.index(default_telegram_dialog_id)
                if dialog_index >= 0:
                    self.dialog_select.current(dialog_index)
                    self.dialog_select_on_select()
        self.trade_port_var.set(trade_port)
        trade_mode = self.config.get_trade_setting("trade_mode")
        trade_product_hsi = self.config.get_trade_setting("trade_product_hsi") == "Y"
        trade_product_mhi = self.config.get_trade_setting("trade_product_mhi") == "Y"
        hsi_trade_quantity = self.config.get_trade_setting("hsi_trade_quantity")
        mhi_trade_quantity = self.config.get_trade_setting("mhi_trade_quantity")
        hsi_margin = self.config.get_trade_setting("hsi_margin")
        mhi_margin = self.config.get_trade_setting("mhi_margin")
        trade_period_morning = self.config.get_trade_setting("trade_period_morning") == "Y"
        trade_period_afternoon = self.config.get_trade_setting("trade_period_afternoon") == "Y"
        trade_period_night = self.config.get_trade_setting("trade_period_night") == "Y"
        open_extra_price = self.config.get_trade_setting("open_extra_price")
        close_price_adjust_interval = self.config.get_trade_setting("close_price_adjust_interval")
        cancel_unfulfilled_order_after_second = self.config.get_trade_setting(
            "cancel_unfulfilled_order_after_second")
        trade_only_within_second = self.config.get_trade_setting("trade_only_within_second")
        manual_confirm_trade_message = self.config.get_trade_setting("manual_confirm_trade_message")
        self.trade_mode_var.set(trade_mode)
        self.trade_product_hsi_var.set(trade_product_hsi)
        self.trade_product_mhi_var.set(trade_product_mhi)
        self.trade_mode_checkbox_on_change()
        self.hsi_trade_quantity_var.set(hsi_trade_quantity)
        self.mhi_trade_quantity_var.set(mhi_trade_quantity)
        self.hsi_margin_var.set(hsi_margin)
        self.mhi_margin_var.set(mhi_margin)
        self.trade_period_morning_var.set(trade_period_morning)
        self.trade_period_afternoon_var.set(trade_period_afternoon)
        self.trade_period_night_var.set(trade_period_night)
        self.open_extra_price_var.set(open_extra_price)
        self.close_price_adjust_interval_var.set(close_price_adjust_interval)
        self.cancel_unfulfilled_order_after_second_var.set(cancel_unfulfilled_order_after_second)
        self.trade_only_within_second_var.set(trade_only_within_second)
        self.manual_confirm_trade_message_var.set(manual_confirm_trade_message)

    def dialog_select_on_select(self, var=''):
        self.selected_dialog_id = self.telegram_dialog_list[self.dialog_select.current()]['id']
        self.config.save_default_telegram_dialog_id(self.selected_dialog_id)
        self.enable_elements(
            self.dialog_save_setting_button, self.dialog_test_button, self.open_buy_template_entry,
            self.close_buy_template_entry, self.open_sell_template_entry, self.close_sell_template_entry,
            self.time_format_entry
        )
        dialog_setting = self.config.get_telegram_dialog_setting(self.selected_dialog_id)
        if dialog_setting is not None:
            self.open_buy_template_var.set(dialog_setting['open_buy_template'])
            self.close_buy_template_var.set(dialog_setting['close_buy_template'])
            self.open_sell_template_var.set(dialog_setting['open_sell_template'])
            self.close_sell_template_var.set(dialog_setting['close_sell_template'])
            self.time_format_var.set(dialog_setting['time_format'])
        else:
            self.open_buy_template_var.set('')
            self.close_buy_template_var.set('')
            self.open_sell_template_var.set('')
            self.close_sell_template_var.set('')
            self.time_format_var.set('')

    async def refresh_dialog_list(self, *args):
        pass

    async def test_dialog_setting(self, *args):
        pass

    def save_dialog_setting(self):
        if self.selected_dialog_id is not None:
            self.disable_elements(self.dialog_save_setting_button)
            self.config.save_telegram_dialog_setting(self.selected_dialog_id,
                                                     self.open_buy_template_entry.get(),
                                                     self.close_buy_template_entry.get(),
                                                     self.open_sell_template_entry.get(),
                                                     self.close_sell_template_entry.get(),
                                                     self.time_format_entry.get()
                                                     )
            self.config.save()
            self.console_write_line("成功儲存頻道訊息設定")
            messagebox.showinfo("頻道設定", "成功儲存訊息設定")
            self.dialog_save_setting_button.after(100, self.enable_elements(self.dialog_save_setting_button))

    @staticmethod
    def enable_elements(*elements):
        for element in elements:
            if type(element) == tk.ttk.Combobox:
                element['state'] = "readonly"
            else:
                element['state'] = tk.NORMAL

    @staticmethod
    def disable_elements(*elements):
        for element in elements:
            element['state'] = tk.DISABLED

    def trade_port_entry_on_change(self, sv):
        max_port_length = 5
        port = sv.get()
        port = ''.join([n for n in port if n.isdigit()])
        sv.set(port)
        if len(port) > max_port_length:
            port = port[:max_port_length]
            sv.set(port)
        if self.config.get_trade_port() != port:
            self.config.save_trade_port(port)

    def trade_setting_entry_on_change(self, sv, code, value_type):
        value = sv.get()
        if value_type == constants.TkinterEntryType.POSITIVE_INTEGER:
            value = ''.join([n for n in value if n.isdigit()])
        elif value_type == constants.TkinterEntryType.INTEGER:
            value = ''.join([value[i] for i in range(len(value))
                             if value[i].isdigit() or (i == 0 and value[i] == "-")])
        elif value_type == constants.TkinterEntryType.FLOAT:
            has_dot = False
            values = []
            for n in value:
                if n.isdigit():
                    values.append(n)
                elif n == "." and has_dot is False:
                    has_dot = True
                    values.append(n)
            value = ''.join(values)
        sv.set(value)
        if self.config.get_trade_setting(code) != value:
            self.config.set_trade_setting(code, value)
            self.config.save()

    async def validate_trade_account_setting(self):
        pass

    async def test_trade_account_setting(self, *args):
        pass

    def get_raw_trade_settings(self):
        trade_mode = self.trade_mode_var.get()
        trade_product_hsi = self.trade_product_hsi_var.get()
        trade_product_mhi = self.trade_product_mhi_var.get()
        hsi_trade_quantity = self.hsi_trade_quantity_var.get()
        mhi_trade_quantity = self.mhi_trade_quantity_entry.get()
        hsi_margin = self.hsi_margin_var.get()
        mhi_margin = self.mhi_margin_var.get()
        trade_period_morning = self.trade_period_morning_var.get()
        trade_period_afternoon = self.trade_period_afternoon_var.get()
        trade_period_night = self.trade_period_night_var.get()
        open_extra_price = self.open_extra_price_var.get()
        close_price_adjust_interval = self.close_price_adjust_interval_var.get()
        cancel_unfulfilled_order_after_second = self.cancel_unfulfilled_order_after_second_var.get()
        trade_only_within_second = self.trade_only_within_second_var.get()
        manual_confirm_trade_message = self.manual_confirm_trade_message_var.get()
        return {
            'trade_mode': trade_mode,
            'trade_product_hsi': trade_product_hsi,
            'trade_product_mhi': trade_product_mhi,
            'hsi_trade_quantity': hsi_trade_quantity,
            'mhi_trade_quantity': mhi_trade_quantity,
            'hsi_margin': hsi_margin,
            'mhi_margin': mhi_margin,
            'trade_period_morning': trade_period_morning,
            'trade_period_afternoon': trade_period_afternoon,
            'trade_period_night': trade_period_night,
            'open_extra_price': open_extra_price,
            'close_price_adjust_interval': close_price_adjust_interval,
            'cancel_unfulfilled_order_after_second': cancel_unfulfilled_order_after_second,
            'trade_only_within_second': trade_only_within_second,
            'manual_confirm_trade_message': manual_confirm_trade_message
        }

    async def validate_trade_setting(self, *args):
        pass

    def trade_mode_checkbox_on_change(self, force_update=False):
        trade_mode = self.trade_mode_var.get()
        if force_update is True or trade_mode != self.selected_trade_mode:
            self.selected_trade_mode = trade_mode
            if trade_mode == constants.TradeMode.FIXED_QUANTITY:
                if self.trade_product_hsi_var.get() is True:
                    self.enable_elements(self.hsi_trade_quantity_entry)
                else:
                    self.disable_elements(self.hsi_trade_quantity_entry)
                if self.trade_product_mhi_var.get() is True:
                    self.enable_elements(self.mhi_trade_quantity_entry)
                else:
                    self.disable_elements(self.mhi_trade_quantity_entry)
                self.disable_elements(self.hsi_margin_entry, self.mhi_margin_entry)

            elif trade_mode == constants.TradeMode.MAX_QUANTITY:
                if self.trade_product_hsi_var.get() is True:
                    self.enable_elements(self.hsi_margin_entry)
                else:
                    self.disable_elements(self.hsi_margin_entry)
                if self.trade_product_mhi_var.get() is True:
                    self.enable_elements(self.mhi_margin_entry)
                else:
                    self.disable_elements(self.mhi_margin_entry)
                self.disable_elements(self.hsi_trade_quantity_entry, self.mhi_trade_quantity_entry)
        self.config.set_trade_setting("trade_mode", trade_mode)
        self.config.save()

    def trade_product_checkbox_on_change(self):
        trade_product_hsi = "Y" if self.trade_product_hsi_var.get() is True else "N"
        trade_product_mhi = "Y" if self.trade_product_mhi_var.get() is True else "N"
        self.config.set_trade_setting("trade_product_hsi", trade_product_hsi)
        self.config.set_trade_setting("trade_product_mhi", trade_product_mhi)
        self.config.save()
        self.disable_elements(self.hsi_margin_entry, self.mhi_margin_entry, self.hsi_trade_quantity_entry,
                              self.mhi_trade_quantity_entry)
        trade_mode = self.trade_mode_var.get()
        if trade_mode == constants.TradeMode.FIXED_QUANTITY:
            if trade_product_hsi == "Y":
                self.enable_elements(self.hsi_trade_quantity_entry)
            if trade_product_mhi == "Y":
                self.enable_elements(self.mhi_trade_quantity_entry)

        elif trade_mode == constants.TradeMode.MAX_QUANTITY:
            if trade_product_hsi == "Y":
                self.enable_elements(self.hsi_margin_entry)
            if trade_product_mhi == "Y":
                self.enable_elements(self.mhi_margin_entry)

    def trade_setting_checkbox_on_change(self, value, code):
        value = "Y" if value.get() is True else "N"
        self.config.set_trade_setting(code, value)
        self.config.save()

    def console_insert_empty_line(self):
        self.enable_elements(self.console_text)
        self.console_text.insert(tk.END, "\n")
        self.disable_elements(self.console_text)
        self.console_text.see(tk.END)

    def console_write_line(self, message, tag=""):
        self.enable_elements(self.console_text)
        time_str = utils.get_local_datetime_str_in_default_format()
        self.console_text.insert(tk.END, time_str, constants.TkinterTextColorTag.LogTime.TITLE)
        self.console_text.insert(tk.END, "\t\t")
        if "\n" not in message:
            console_message = (constants.TEXTWRAP_SEPARATOR + " ").join(textwrap.wrap(message, width=65))
        else:
            console_message = message
        self.console_text.insert(tk.END, console_message, tag)
        self.console_text.insert(tk.END, "\n")
        logger.info("[CONSOLE]" + time_str + "   " + message)
        self.run_async_task(self.tg.client.send_message, 'me', f"[TFT] {message}")
        self.disable_elements(self.console_text)
        self.console_text.see(tk.END)

    def console_write_text(self, message, tag="", is_start=False, is_end=False):
        self.enable_elements(self.console_text)
        if is_start:
            time_str = utils.get_local_datetime_str_in_default_format()
            self.console_text.insert(tk.END, time_str, constants.TkinterTextColorTag.LogTime.TITLE)
            self.console_text.insert(tk.END, "\t\t")
            self.console_text_cache = ""
            self.console_text_cache_time = time_str
        log_message = message
        if constants.TEXTWRAP_SEPARATOR in message:
            log_message = message.replace(constants.TEXTWRAP_SEPARATOR, "")
        self.console_text.insert(tk.END, message, tag)
        self.console_text_cache += log_message
        if is_end:
            self.console_text.insert(tk.END, "\n")
            logger.info("[CONSOLE]" + self.console_text_cache_time + "   " + self.console_text_cache)
            self.run_async_task(self.tg.client.send_message, 'me', f"[TFT] {self.console_text_cache}")
            self.console_text_cache = ""
            self.console_text_cache_time = ""
        self.disable_elements(self.console_text)
        self.console_text.see(tk.END)

    def clear_console(self):
        self.enable_elements(self.console_text)
        self.console_text.delete(1.0, tk.END)
        self.disable_elements(self.console_text)

    def async_thread(self, func, *args):
        self.async_loop.run_until_complete(func(*args))

    def run_async_task(self, *args):
        t = threading.Thread(target=self.async_thread, args=args)
        t.daemon = True
        t.start()

    async def start_follow_trade(self, *args):
        pass

    def stop_follow_trade(self):
        pass

    def get_elements_to_be_disabled_on_start_follow_trade(self):
        return (self.dialog_select,
                self.dialog_test_button,
                self.dialog_update_button,
                self.dialog_save_setting_button,
                self.open_buy_template_entry,
                self.close_buy_template_entry,
                self.open_sell_template_entry,
                self.close_sell_template_entry,
                self.time_format_entry,
                self.trade_password_entry,
                self.trade_port_entry,
                self.trade_password_test_button,
                self.trade_mode_fixed_quantity,
                self.trade_mode_max_quantity,
                self.trade_product_hsi,
                self.trade_product_mhi,
                self.hsi_trade_quantity_entry,
                self.mhi_trade_quantity_entry,
                self.hsi_margin_entry,
                self.mhi_margin_entry,
                self.trade_period_morning,
                self.trade_period_afternoon,
                self.trade_period_night,
                self.open_extra_price_entry,
                self.close_price_adjust_interval_entry,
                self.cancel_unfulfilled_order_after_second_entry,
                self.trade_only_within_second_entry,
                self.manual_confirm_trade_message)

    def disable_elements_on_start_follow_trade(self):
        self.disable_elements(*self.get_elements_to_be_disabled_on_start_follow_trade())

    def enable_elements_on_stop_follow_trade(self):
        self.enable_elements(*self.get_elements_to_be_disabled_on_start_follow_trade())
        self.trade_mode_checkbox_on_change(True)
