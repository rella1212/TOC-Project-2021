from transitions.extensions import GraphMachine
import os
import pygsheets
import json
from utils import send_text_message
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from linebot.models import MessageEvent, TextMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction, ConfirmTemplate

load_dotenv()

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)
gc = pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS')
sht = gc.open_by_url('https://docs.google.com/spreadsheets/d/1HloG5pAHXrlLvyyiHUef0qYGCQkkBJkwMSt-kqhRWcQ/edit#gid=0')
wks_list = sht.worksheets()
wks = sht[0]

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        self.order_dict = dict(name='Allen', phone='0912345678', people=0, date='1/1', time='09:30')

    def is_going_to_user(self, event):
        text = event.message.text
        return text.lower() == "start"

    def is_going_to_reserve(self, event):
        text = event.message.text
        return text.lower() == "reserve"

    def is_going_to_rest_info(self, event):
        text = event.message.text
        return text.lower() == "branches info"

    def is_going_to_meal_menu(self, event):
        text = event.message.text
        return text.lower() == "meal menu"

    def is_going_to_store1(self, event):
        text = event.message.text
        return text.lower() == "taichung branch"

    def is_going_to_store2(self, event):
        text = event.message.text
        return text.lower() == "tainan branch"

    def on_enter_user(self, event):
        print("I'm entering user")
        line_bot_api.push_message(event.source.user_id, TemplateSendMessage(
                            alt_text='Buttons template',
                            template=ButtonsTemplate(
                                title='Welcome to KFP!',
                                text='Please choose the function',
                                thumbnail_image_url='https://i.imgur.com/x4WvPaW.jpeg',
                                image_aspect_ratio='rectangle',
                                actions=[
                                    MessageTemplateAction(
                                        label='Reserve',
                                        text='Reserve'
                                    ),
                                    MessageTemplateAction(
                                        label='Branches info',
                                        text='Branches info'
                                    ),
                                    MessageTemplateAction(
                                        label='Meal menu',
                                        text='Meal menu'
                                    ),
                                ]
                            )
                        ))

    def on_enter_reserve(self, event):
        print("I'm entering order")

        reply_token = event.reply_token
        send_text_message(reply_token, "Please enter your name.\nEx: Allen")

    def on_enter_rest_info(self, event):
        print("I'm entering rest_info")

        reply_token = event.reply_token
        line_bot_api.reply_message(reply_token, TemplateSendMessage(
                            alt_text='Buttons template',
                            template=ButtonsTemplate(
                                title='Branch Information',
                                text='Please choose one of the branches',
                                actions=[
                                    MessageTemplateAction(
                                        label='Taichung Branch',
                                        text='Taichung Branch'
                                    ),
                                    MessageTemplateAction(
                                        label='Tainan Branch',
                                        text='Tainan Branch'
                                    )
                                ]
                                )
                            )
                            )

    def on_enter_meal_menu(self, event):
        print("I'm entering meal_menu")
        reply_token = event.reply_token
        send_text_message(reply_token, "https://kiarafriedphoenix.com/menu")
        self.go_back(event)
    
    def cancel_reserve(self, event):
        text = event.message.text
        if text.lower() == "cancel this reservation"
            return True
        else:
            return False

    def accept_name(self, event):
        text = event.message.text
        if text.lower() == "cancel this reservation":
            return False
        else:
            self.order_dict["name"] = text
            return True
    

    def on_enter_ask_phone(self, event):
        print("I'm entering ask phone")
        reply_token = event.reply_token
        send_text_message(reply_token, "Please enter your phone.\nEx: 0912345678")

    def accept_phone(self, event):
        text = event.message.text
        if text.lower() == "cancel this reservation":
            return False
        else:
            self.order_dict["phone"] = text
            return True

    def on_enter_ask_people(self, event):
        print("I'm entering ask people")
        reply_token = event.reply_token
        send_text_message(reply_token, "Please enter the number of people.\nEx: 4")

    def accept_people(self, event):
        text = event.message.text
        if text.lower() == "cancel this reservation":
            return False
        else:
            self.order_dict["people"] = int(text)
            return True

    def on_enter_ask_date(self, event):
        print("I'm entering ask date")
        reply_token = event.reply_token
        send_text_message(
            reply_token, "Please enter the date you want to reserve.\nEx: 1/1\n\n[Notice]: you can only reserve the date in this month.")

    def accept_date(self, event):
        text = event.message.text
        if text.lower() == "cancel this reservation":
            return False
        else:
            date = text
            date_list = date.split('/')
            if date_list[0] != "1":
                line_bot_api.push_message(event.source.user_id, TextSendMessage(
                    text="You can only reserve the date in this month.\nPlease choose again."))
                return False
            elif int(date_list[1]) > 31 or int(date_list[1]) < 1:
                line_bot_api.push_message(event.source.user_id, TextSendMessage(
                    text="Wrong input\nPlease choose again."))
                return False
            else:
                self.order_dict["date"] = text
                return True

    def on_enter_ask_time(self, event):
        print("I'm entering ask time")
        date = self.order_dict['date']
        date_list = date.split('/')
        day = int(date_list[1])
        day_reserve = wks.get_values(start=(
            2, day+1), end=(13, day+1), include_tailing_empty=True, include_tailing_empty_rows=True)
        s1 = 'The day reservation: '+date+'\n'
        for i in range(len(day_reserve)):
            x = day_reserve[i]
            if x == ['']:
                if i == 0:
                    s1 += '0'+str(i+9)+':30  Empty\n'
                else:
                    s1 += str(i+9)+':30  Empty\n'
            else:
                if i == 0:
                    s1 += '0'+str(i+9)+':30  Reserved\n'
                else:
                    s1 += str(i+9)+':30  Reserved\n'
        reply_token = event.reply_token
        send_text_message(
            reply_token, s1+"\nPlease enter the time you want to reserve.\nEx: 9:30")

    def accept_time(self, event):
        text = event.message.text
        if text.lower() == "cancel this reservation":
            return False
        else:
            date = self.order_dict['date']
            date_list = date.split('/')
            day = int(date_list[1])
            hour = text
            hour_list = hour.split(':')
            h = int(hour_list[0]) - 7
            time_reserve = wks.get_value((h, day+1))
            print(time_reserve)
            if time_reserve == "":
                self.order_dict["time"] = text
                return True
            else:
                line_bot_api.push_message(event.source.user_id, TextSendMessage(
                    text="This time interval is reserved.\nPlease choose another time interval."))
                return False

    def on_enter_check_reserve(self, event):
        print("I'm entering check reservation")
        reply_token = event.reply_token
        reservation_info = "This is your reservation:\n\n"
        name = "Name: " + self.order_dict['name'] + "\n"
        phone = "Phone: " + self.order_dict['phone'] + "\n"
        people = "People: " + str(self.order_dict['people']) + "\n"
        date = "Date: " + self.order_dict['date'] + "\n"
        time = "Time: " + self.order_dict['time']
        reservation_info = reservation_info + name + people + date + time
        line_bot_api.push_message(
            event.source.user_id, TextSendMessage(text=reservation_info))
        line_bot_api.push_message(event.source.user_id, TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                title='Is your reservation correct?',
                text='Is your reservation correct?',
                actions=[
                    MessageTemplateAction(
                        label='Correct',
                        text='Correct'
                    ),
                    MessageTemplateAction(
                        label='Incorrect',
                        text='Incorrect'
                    )
                ]
            )
        )
        )

    def reserve_correct(self, event):
        text = event.message.text
        if text.lower() == "cancel this reservation":
            return False
        else:
            if text.lower() == "correct":
                hour = self.order_dict['time']
                hour_list = hour.split(':')
                h = int(hour_list[0]) - 7
                date = self.order_dict['date']
                date_list = date.split('/')
                day = int(date_list[1])
                x = wks.get_value((h, day+1))
                if x == "":
                    wks.update_value(addr=(h, day+1), val=(self.order_dict['name']+'\n'+self.order_dict['phone']+'\n'+str(self.order_dict['people'])))
                    line_bot_api.push_message(event.source.user_id, TextSendMessage(text='Your reservation is confirmed.\nHave a nice day!'))
                    return True
                else:
                    line_bot_api.push_message(event.source.user_id, TextSendMessage(text='The reservation is failed.\nThe time you choose has been reserved.\nBack to menu.'))
                    return True
            else:
                return False

    def reserve_incorrect(self, event):
        text = event.message.text
        if text.lower() == "incorrect":
            line_bot_api.push_message(event.source.user_id, TextSendMessage(
                text='Restart the reservation process.'))
        return text.lower() == "incorrect"

    def on_enter_store1_info(self, event):
        print("I'm entering store1")
        reply_token = event.reply_token
        send_text_message(reply_token, "Store1_info")
        self.go_back(event)

    def on_enter_store2_info(self, event):
        print("I'm entering store2")
        reply_token = event.reply_token
        send_text_message(reply_token, "Store2_info")
        self.go_back(event)
