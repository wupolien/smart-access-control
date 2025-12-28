from gpiozero import Buzzer
from time import sleep

b = Buzzer(20)

while True:
    b.on()
    sleep(1)
    b.off()
    sleep(1)
