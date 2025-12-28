from gpiozero import MotionSensor
from time import sleep

pir = MotionSensor(17)

print("PIR 測試開始，靠近感應器看看...")
while True:
    if pir.motion_detected:
        print("有人靠近！")
    else:
        print("沒人")
    sleep(0.5)
