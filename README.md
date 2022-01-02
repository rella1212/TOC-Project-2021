# TOC Project 2021 - KFP Reservation Bot

## 介紹
我這次製作的是一個虛擬餐廳的line Chat bot，可以使用這個lineBot向店家訂位、查詢這個餐廳的分店資訊及確認菜單。

## 環境
* Python 3.7.0
* Windows 10

## 技術
* Deploy with Heroku and git
    * This bot runs on the cloud server.
* GoogleSheet API、pygsheets
    * Connect this bot and the googlesheet in the cloud drive. 
## 使用說明
1. 輸入 Start 開始
    ![](https://i.imgur.com/QxN9W0K.png)

3. 選擇你需要的服務
    * 訂位
         1. 輸入：姓名、電話、人數、日期
         2. 選擇要預訂的時段
         3. 確認訂位資訊是否正確
         4. 完成訂位
         ![](https://i.imgur.com/sroe13D.jpg)
         * ![](https://i.imgur.com/uCiG8Cj.png)

    * 查詢餐廳
         1. 選擇分店
         2. 完成
         ![](https://i.imgur.com/3AVqH1M.jpg)

    * 查看菜單 
         ![](https://i.imgur.com/C2wFfXR.png)


* Reservation datasheet: https://docs.google.com/spreadsheets/d/1HloG5pAHXrlLvyyiHUef0qYGCQkkBJkwMSt-kqhRWcQ/edit#gid=0


## FSM of this bot

![](https://i.imgur.com/8rvchiL.png)

### State介紹
主要的State:
* start: 輸入start就會到user
* user: 選擇功能
* reserve: 訂位
    * substate: ask_phone -> ask_people -> ask_date, -> ask_time -> check_correct
    * 這幾個state都可以輸入"cancel this reservation"回到user state
    * 在 check correct state, 如果回覆correct會回到user state,回覆incorrect則會回到reserve state
* rest_info: 查詢店家資訊
    * substate: store1_info, store2_info
    * 顯示完資訊就回到user state 
* meal_menu: 看菜單
    * 顯示完菜單就回到user state 

## GoogleSheet API 的使用

![](https://i.imgur.com/dZKIidk.png)
* 使用Google cloud platform管理專案

1. 建立專案
2. 啟用API
3. 新增管理此專案的帳號
4. 獲得金鑰(放置於.env)
5. 設定管理帳號共用datasheet
6. 在程式中使用此金鑰連結至datasheet

```python
# 連結範例
gc = pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS')
sht = gc.open_by_url('datasheet的網址')

# 由於金鑰是JSON格式
# 要將金鑰放到.env時須有一個KEY為 'GDRIVE_API_CREDENTIALS'
# 這個key的value即為整個JSON檔的內容
```
## 特別處理
1. 可以多人同時使用這個line bot, 每個user有自己的state machine, 不會互相影響。
2. 訂位系統只能訂當月的日期，無法選擇已被預訂的時段。
3. 訂位系統在check_correct state時仍會再次確認此日期時間是否被預訂，防止有其他人已經於同時段訂位成功卻覆蓋訂位的狀況。(Multi-threads: avoiding race condition)

## 總結

這次的linebot最主要就是想寫訂位系統，並使用雲端的試算表紀錄訂位。

過程中在處理Heroku的環境遇到不少問題，後來調整了pipenv的python版本到和local端一樣的3.7.0，並且把package都重新安裝過就解決了。

而googlesheet api跟pygsheets也花了蠻多時間研究的，因為要搬到heroku上面也可以執行，加上金鑰是JSON檔，找處理方式花了蠻多時間的。


## Reference

### linebot
* https://developers.line.biz/en/docs/messaging-api/
* https://github.com/line/line-bot-sdk-python

### Heroku
* https://devcenter.heroku.com/categories/python-support


### GoogleSheet API
* https://developers.google.com/sheets/api/reference/rest
* https://www.learncodewithmike.com/2020/08/python-write-to-google-sheet.html







