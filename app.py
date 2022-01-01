import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction

from fsm import TocMachine
from utils import send_text_message

load_dotenv()


machine = TocMachine(
    states=["start", "user", "reserve", "rest_info", "meal_menu", "ask_phone",
            "ask_people", "ask_date", "ask_time", "check_reserve", "store1_info", "store2_info"],
    transitions=[
        {
            "trigger": "advance",
            "source": "start",
            "dest": "user",
            "conditions": "is_going_to_user",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "reserve",
            "conditions": "is_going_to_reserve",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "rest_info",
            "conditions": "is_going_to_rest_info",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "meal_menu",
            "conditions": "is_going_to_meal_menu",
        },
        {
            "trigger": "advance",
            "source": "rest_info",
            "dest": "store1_info",
            "conditions": "is_going_to_store1",
        },
        {
            "trigger": "advance",
            "source": "rest_info",
            "dest": "store2_info",
            "conditions": "is_going_to_store2",
        },
        {
            "trigger": "advance",
            "source": "reserve",
            "dest": "ask_phone",
            "conditions": "accept_name",
        },
        {
            "trigger": "advance",
            "source": "ask_phone",
            "dest": "ask_people",
            "conditions": "accept_phone",
        },
        {
            "trigger": "advance",
            "source": "ask_people",
            "dest": "ask_date",
            "conditions": "accept_people",
        },
        {
            "trigger": "advance",
            "source": "ask_date",
            "dest": "ask_time",
            "conditions": "accept_date",
        },
        {
            "trigger": "advance",
            "source": "ask_time",
            "dest": "check_reserve",
            "conditions": "accept_time",
        },
        {
            "trigger": "advance",
            "source": "check_reserve",
            "dest": "user",
            "conditions": "reserve_correct",
        },
        {
            "trigger": "advance",
            "source": "check_reserve",
            "dest": "reserve",
            "conditions": "reserve_incorrect",
        },

        {"trigger": "go_back",
            "source": ["store1_info", "store2_info", "meal_menu"],
            "dest": "user"
         },
    ],
    initial="start",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "Not Correct input")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
