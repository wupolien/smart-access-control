from lcd_driver import LCD
import time

lcd = LCD(2, 0x27, True)
lcd.message("HELLO", 1)
lcd.message("LCD OK", 2)

time.sleep(10)

# Clear the LCD display
lcd.clear()
