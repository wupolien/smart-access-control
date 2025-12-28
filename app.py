#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import time
import threading

from dotenv import load_dotenv
from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 硬體
from gpiozero import LED, Buzzer, MotionSensor, Servo
from lcd_driver import LCD

# ------------------ 初始設定 ------------------ #
load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_NOTIFY_USER_ID = os.getenv("LINE_NOTIFY_USER_ID")  # 你的 LINE user_id

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET or not LINE_NOTIFY_USER_ID:
    print("請先設定 .env 中的 LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, LINE_NOTIFY_USER_ID")
    sys.exit(1)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# ------------------ GPIO 設定 ------------------ #
pir = MotionSensor(17)
green_led = LED(16)
red_led = LED(21)
buzzer = Buzzer(20)
door_servo = Servo(12, initial_value=None)  # 啟動時不動
lcd = LCD(2, 0x27, True)

# ------------------ 密碼設定 ------------------ #
CORRECT_PASSWORD = "1234"

# ------------------ 狀態控制 ------------------ #
waiting_for_password = False
lock = threading.Lock()

# ------------------ 平滑控制馬達 ------------------ #
def smooth_servo(servo, start, end, duration=1.0, steps=20):
    delta = (end - start) / steps
    delay = duration / steps
    for i in range(steps+1):
        servo.value = start + delta * i
        time.sleep(delay)

# ------------------ PIR 偵測線程 ------------------ #
def pir_thread():
    global waiting_for_password
    while True:
        pir.wait_for_motion()
        with lock:
            if waiting_for_password:
                continue
            waiting_for_password = True

        # LCD 顯示
        lcd.message("Password please", 1)
        print("PIR triggered: waiting for password")

        # LINE Bot 發訊息
        try:
            line_bot_api.push_message(
                LINE_NOTIFY_USER_ID,
                TextSendMessage(text="🚨 有人靠近智慧門禁！請輸入密碼。")
            )
        except Exception as e:
            print(f"LINE Bot 推播失敗: {e}")

        pir.wait_for_no_motion()
        time.sleep(0.5)

# ------------------ 開門 / 警示 ------------------ #
def process_access(success: bool, user_id=None):
    global waiting_for_password
    if success:
        lcd.message("Access Granted", 1)
        green_led.on()

        # 平滑開門
        smooth_servo(door_servo, 0, -1, duration=1.0)  # mid -> min

        # LINE Bot 通知
        if user_id:
            try:
                line_bot_api.push_message(user_id, TextSendMessage(text="✅ 開門成功！"))
            except Exception as e:
                print(f"LINE Bot 發訊息失敗: {e}")

        # LCD 倒數關門
        open_time = 5
        for i in range(open_time, 0, -1):
            lcd.message(f"Closing in {i}s", 2)
            time.sleep(1)

        # 平滑關門
        smooth_servo(door_servo, -1, 0, duration=1.0)  # min -> mid
        green_led.off()
    else:
        lcd.message("Access Denied", 1)
        red_led.on()
        buzzer.on()
        if user_id:
            try:
                line_bot_api.push_message(user_id, TextSendMessage(text="❌ 密碼錯誤！"))
            except Exception as e:
                print(f"LINE Bot 發訊息失敗: {e}")
        time.sleep(3)
        red_led.off()
        buzzer.off()

    lcd.clear()
    waiting_for_password = False

# ------------------ Flask & LINE Webhook ------------------ #
@app.route("/", methods=["GET"])
def index():
    return "LINE Bot Running", 200

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
    user_text = event.message.text.strip()
    user_id = event.source.user_id

    global waiting_for_password
    if waiting_for_password:
        if user_text == CORRECT_PASSWORD:
            threading.Thread(target=process_access, args=(True, user_id), daemon=True).start()
        else:
            threading.Thread(target=process_access, args=(False, user_id), daemon=True).start()
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text="尚未偵測到人靠近，請靠近感應器再輸入密碼。"
        ))

# ------------------ 主程式 ------------------ #
if __name__ == "__main__":
    # 啟動 PIR 偵測線程
    threading.Thread(target=pir_thread, daemon=True).start()
    
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
