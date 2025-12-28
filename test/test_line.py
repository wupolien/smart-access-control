#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import threading
import time
from flask import Flask, request, abort
from gpiozero import MotionSensor, LED, Buzzer
from lcd_driver import LCD
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# ------------------ 初始化 ------------------ #
load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

app = Flask(__name__)

# ------------------ GPIO 設定 ------------------ #
pir = MotionSensor(17)
green_led = LED(16)
red_led = LED(21)
buzzer = Buzzer(20)
door = LED(12)  # 繼電器控制門
lcd = LCD(2, 0x27, True)

# ------------------ 密碼設定 ------------------ #
CORRECT_PASSWORD = "1234"

# ------------------ 狀態變數 ------------------ #
waiting_for_password = False
lock = threading.Lock()
current_user_id = None

# ------------------ PIR 偵測線程 ------------------ #
def pir_thread():
    global waiting_for_password, current_user_id
    while True:
        pir.wait_for_motion()
        with lock:
            if waiting_for_password:
                continue
            waiting_for_password = True
        lcd.message("Password please", 1)
        print("PIR triggered: waiting for password")
        # 可在這裡透過 LINE broadcast / push 通知使用者
        pir.wait_for_no_motion()
        time.sleep(0.5)

# ------------------ 處理開門 / 警示 ------------------ #
def process_access(success: bool, user_id):
    global waiting_for_password
    if success:
        lcd.message("Access Granted", 1)
        green_led.on()
        door.on()
        line_bot_api.push_message(user_id, TextSendMessage(text="✅ 開門成功！"))
        time.sleep(5)
        green_led.off()
        door.off()
    else:
        lcd.message("Access Denied", 1)
        red_led.on()
        buzzer.on()
        line_bot_api.push_message(user_id, TextSendMessage(text="❌ 密碼錯誤！"))
        time.sleep(3)
        red_led.off()
        buzzer.off()
    lcd.clear()
    waiting_for_password = False

# ------------------ Flask 與 LINE Webhook ------------------ #
@app.route("/", methods=["GET"])
def index():
    return "LINE Bot Running", 200

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
    global waiting_for_password, current_user_id
    user_text = event.message.text.strip()
    user_id = event.source.user_id
    current_user_id = user_id

    if waiting_for_password:
        threading.Thread(target=process_access, args=(user_text == CORRECT_PASSWORD, user_id), daemon=True).start()
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="尚未偵測到人靠近，請靠近感應器再輸入密碼。")
        )

# ------------------ 主程式 ------------------ #
if __name__ == "__main__":
    threading.Thread(target=pir_thread, daemon=True).start()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
