from transitions.extensions import GraphMachine
import os
from utils import send_text_message 
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from linebot.models import MessageEvent, TextMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction

load_dotenv()

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        self.order_dict = dict(name='Allen', phone='0912345678', people=0, date='1/1',time='09:30')

    def is_going_to_user(self, event):
        text = event.message.text
        return text.lower() == "start"

    def is_going_to_reserve(self, event):
        text = event.message.text
        return text.lower() == "reserve"

    def is_going_to_rest_info(self, event):
        text = event.message.text
        return text.lower() == "stores info"

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
                                actions=[
                                    MessageTemplateAction(
                                        label='Reserve',
                                        text='Reserve'
                                    ),
                                    MessageTemplateAction(
                                        label='Stores info',
                                        text='Stores info'
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
        send_text_message(reply_token, "Menu")
        self.go_back(event)

    def accept_name(self, event):
        text = event.message.text
        self.order_dict["name"] = text
        return True
    
    def on_enter_ask_phone(self, event):
        print("I'm entering ask phone")
        reply_token = event.reply_token
        send_text_message(reply_token, "Please enter your phone.\nEx: 0912345678")

    def accept_phone(self, event):
        text = event.message.text
        self.order_dict["phone"] = text
        return True

    def on_enter_ask_people(self, event):
        print("I'm entering ask people")
        reply_token = event.reply_token
        send_text_message(reply_token, "Please enter the number of people.\nEx: 4")

    def accept_people(self, event):
        text = event.message.text
        self.order_dict["people"] = int(text)
        return True
    
    def on_enter_ask_date(self, event):
        print("I'm entering ask date")
        reply_token = event.reply_token
        send_text_message(reply_token, "Please enter the date you want to reserve.\nEx: 1/1")

    def accept_date(self, event):
        text = event.message.text
        self.order_dict["date"] = text
        return True

    def on_enter_ask_time(self, event):
        print("I'm entering ask time")
        reply_token = event.reply_token
        send_text_message(reply_token, "Please enter the time you want to reserve.\nEx: 9:30")

    def accept_time(self, event):
        text = event.message.text
        self.order_dict["time"] = text
        return True

    def on_enter_check_reserve(self, event):
        print("I'm entering check reservation")
        reply_token = event.reply_token
        reservation_info = "This is your reservation:\n\n"
        name = "Name: " + self.order_dict['name'] + "\n"
        phone = "Phone: " + self.order_dict['phone'] + "\n"
        people = "People: " + str(self.order_dict['people']) + "\n"
        date = "Date: " + self.order_dict['date'] + "\n"
        time = "Time: " + self.order_dict['time'] + "\n\n"
        reservation_info = reservation_info + name + people + date + time + "Is it correct?\n(Please answer Correct or Incorrect)"
        send_text_message(reply_token, reservation_info)

    def reserve_correct(self, event):
        text = event.message.text
        if text.lower() == "correct":
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text='Your reservation is confirmed.\nHave a nice day!'))
        return text.lower() == "correct"

    def reserve_incorrect(self, event):
        text = event.message.text
        if text.lower() == "incorrect":
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text='Restart the reservation process.'))
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


