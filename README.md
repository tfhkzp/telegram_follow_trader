# Telegram Follow Trader (TFT)
本程式用於連接Telegram收取用戶指定的頻道或bot的訊息，並參考訊息及按照用戶設定向證券交易服務進行下訂單、改訂單、取消訂單的動作。

## 免責聲明
- 軟件屬於免費開源軟件，用於收取閣下指定的Telegram頻道或bot的訊息，並參考訊息及按照閣下的設定向證券交易服務提供者進行下訂單、改訂單、取消訂單的動作。
- 本軟件及本軟件開發者提供的資訊，不得用作任何特定或其他投資或決定的依據。閣下務須運用並僅依據閣下本身的技術及判斷作出投資或決定。
- 本軟件及本軟件開發者在任何情況下均毋須就因為閣下使用或登入本軟件或其任何部份而直接或間接招致的任何損失或損害(包括相應產生或附帶，特別或懲罰性的損失)，包括因為(但不限於)本軟件的任何缺陷、錯誤、遺留、瑕疵、失誤、錯失或不準確，而招致的任何損失、損害或開支，向閣下或任何其他人士承擔法律責任。
- 本軟件基於（現況）及（現有）提供，不保證毫無錯誤。
- 本軟件及本軟件開發者對一切事項皆不作出任何保證及不承擔任何責任，包括但不限於:
  - 本軟件為準確、現行或可靠
  - 本軟件的缺陷將予糾正
  - 第三方服務或第三方訊息提供者的穩定性及準確性

## 預覽
<img src="https://github.com/tfhkzp/telegram_follow_trader/blob/master/image/tft_main.png" width="600"></img>

## 作業系統
- Windows 10
- macOS 10.15

## 支援證券交易服務提供者
- [X] 富途證券
- [ ] SP Trader


## 使用教學
#### 使用前準備
- Telegram API ID及API Hash
  - 如沒有, 請到https://my.telegram.org 申請<br>
- FutuOpenD
  - 如沒有, 請到富途證券https://www.futunn.com/download/openAPI?lang=zh-hk 下載
- 填寫富途證券API 問卷評估與協議確認
  - 如未填寫, 請到https://www.futunn.com/about/api-disclaimer?lang=zh-hk 填寫 <br>
<img src="https://github.com/tfhkzp/telegram_follow_trader/blob/master/image/futu_form.png" width="400"></img><br>

#### 開啟程式
- 你可以下載程式直接使用
- **或** 下載Source code後運行以下command使用:
```
py trade_app.py
```

#### 開啟FutuOpenD
- 登入FutuOpenD

#### 登入Telegram
<img src="https://github.com/tfhkzp/telegram_follow_trader/blob/master/image/tft_login.png" width="300"></img><br>
TFT**不會**儲存你的API ID, API Hash及電話號碼 <br>
*請小心保管，不要傳送給任何人*

#### 輸入驗證碼
<img src="https://github.com/tfhkzp/telegram_follow_trader/blob/master/image/tft_verify.png" width="300"></img><br>
輸入Telegram發送給你的驗證碼後按確定，通過Telegram的驗證後將會進入主界面。

#### 輸入密碼 (Two-Step verifiction)
<img src="https://github.com/tfhkzp/telegram_follow_trader/blob/master/image/tft_password.png" width="300"></img><br>
如已設定Two-Step Verification，你需要輸入你的Telegram密碼，通過Telegram的驗證後將會進入主界面。

#### 進入主界面
進入主界面後，你可以進行以下設定:
- 選擇頻道並輸入訊息範本
  - 然後按下測試，程式將於比對頻道最近200條訊息，確保找到符合範本的訊息。
  - 轉換教學:
> 建好倉訊息: 04-Aug-2020 17:22:22.440 (20080423): Beta 已於24931點建HSI2008好倉<br>
> 轉換成: ${time} (${trade_id}): Beta 已於${price}點建${product_code}好倉

> 平好倉訊息: 04-Aug-2020 17:44:12.426 (20080423): Beta 已於24931點平HSI2008好倉<br>
> 轉換成: ${time} (${trade_id}): Beta 已於${price}點平${product_code}好倉

> 建淡倉訊息: 04-Aug-2020 09:37:05.377 (20080407): Beta 已於24613點建HSI2008淡倉<br>
> 轉換成: ${time} (${trade_id}): Beta 已於${price}點建${product_code}淡倉

> 平淡倉訊息: 04-Aug-2020 09:45:03.981 (20080407): Beta 已於24538點平HSI2008淡倉<br>
> 轉換成: ${time} (${trade_id}): Beta 已於${price}點平${product_code}淡倉

> 時間格式: %d-%b-%Y %H:%M:%S.%f
- 輸入交易密碼並測試連接
  - 本程式**不會**儲存你的交易密碼
- 交易設定
  - 選擇交易模式
    - 固定交易數量
    - 自動檢測最大交易數量
  - 交易產品
  - 交易數量
  - 交易時段
  - 建倉追價
    - 根據交易記錄訊息再**加**多少溢價進行建倉
    > 例如**建好倉**追價為5，價格為24000，將下單以24005**買入**。 <br>
    > 例如**建淡倉**追價為5，價格為24000，將下單以23995**賣出**。
  - 平倉調整價格區間
    - 當平倉訂單未完成時，將每0.2秒**加**多少溢價修改訂單，確保能成功平倉
    > 例如平倉調整價格區間為1，價格為24000，在**平好倉**時將會24000, 23999, 23998 如此類推一直修改訂單，直至全部交易完畢。 <br>
    > 例如平倉調整價格區間為1，價格為24000，在**平淡倉**時將會24000, 24001, 24002 如此類推一直修改訂單，直至全部交易完畢。
  - 指定秒數後自動取消未成功的建倉交易
  - 忽略延誤指定秒數以上的建倉交易
  - 手動或自動確認交易

## 頻道需求
- 沒有過夜交易(每日的所有開倉都需要於交易時段結束前進行**平倉**)
- 交易記錄訊息需包含:
  - 交易時間(time)
  - 產品編號(product_code) **或** 產品月份(month)
  - 交易編號(trade_id) - 平倉的交易記錄的編號需要跟建倉記錄的編號相同
  - 成交價格(price)

## 開發環境
- Python 3.7.7
- futu-api 3.22.0
- nest-asyncio 1.3.3
- Telethon 1.16.0
- requests 2.24.0

