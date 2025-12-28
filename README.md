# Smart Access Control System

This project presents a Raspberry Pi–based smart access control system integrating a PIR sensor, LCD display, servo motor, LEDs, buzzer, and the LINE Messaging API. The system automatically initiates authentication when human presence is detected and provides real-time feedback and notifications via LINE.

---

## 1. System Features

- Automatic human detection using PIR sensor 
- LCD displays system prompts  
- Password authentication via LINE Messaging API  
- Successful authentication triggers door opening and notification
- Failed authentication triggers alarm and warning notification 

---

## 2. System Architecture

The system architecture consists of three layers:

- **Sensing Layer**：PIR motion sensor 
- **Control Layer**：Raspberry Pi（Python）  
- **Communication Layer**：LINE Messaging API（Webhook + HTTP）  

---

## 3. Hardware Requirements

- Raspberry Pi  
- PIR Motion Sensor 
- LCD 1602（I2C）  
- SG90 Servo Motor 
- LED（red / green）  
- Buzzer
- Use an external 5V power supply (recommended for powering the motor).  

---

## 4. Hardware Wiring (GPIO Configuration)

### GPIO Pin Mapping

| Hardware Module | Function | GPIO Pin |
|-----------------|----------|----------|
| PIR Sensor | Signal (OUT) | GPIO17 |
| PIR Sensor | VCC | 5V |
| PIR Sensor | GND | GND |
| LCD 1602 (I2C) | SDA | GPIO2 (SDA) |
| LCD 1602 (I2C) | SCL | GPIO3 (SCL) |
| LCD 1602 (I2C) | VCC | 5V |
| LCD 1602 (I2C) | GND | GND |
| Green LED | Anode (+) | GPIO16 |
| Red LED | Anode (+) | GPIO21 |
| LED | Cathode (-) | GND (with resistor) |
| Buzzer | Control | GPIO20 |
| Buzzer | GND | GND |
| Servo Motor (SG90) | Signal (Orange) | GPIO12 |
| Servo Motor (SG90) | VCC (Red) | External 5V |
| Servo Motor (SG90) | GND (Brown) | GND |

---

### Notes

- Use an external power supply for the servo motor.  
- LEDs must be connected with current-limiting resistors. 
- Ensure all modules share a common ground (GND).  

---

## 5. Software Requirements

- Python 3.9 or above  
- smbus2
- Flask  
- gpiozero  
- python-dotenv  
- line-bot-sdk  

Install dependencies:

```bash
pip install -r requirements.txt
```

### Enable the I²C Interface

- Execute `sudo raspi-config`.
- Use the up/down keys and Enter to select 3 Interface Options.
- Select I5 I2C.
- When asked whether to enable I2C, use the left/right keys and 
-nter to select `Yes`.
- Press Enter on `OK`.
- Use Tab, the left/right keys, and Enter to select `Finish` to exit raspi-config.
- Reboot the Raspberry Pi.

---

## 6. Environment settings

### Please create a `.env file` with the following content:

```env
LINE_CHANNEL_ACCESS_TOKEN=你的TOKEN
LINE_CHANNEL_SECRET=你的SECRET
LINE_NOTIFY_USER_ID=你的USER_ID
PORT=5000
```
### Create a New Messaging API Channel
- Login to LINE Developers Console.
- https://developers.line.biz/en/
- Create a new Provider in LINE Developers Console.
- Create a new Messaging API channel in the Provider.
- From August 14, 2024, you need to create Messaging API 
channels by creating a LINE Official Account and then 
enabling the use of the Messaging API in the LINE Official 
Account Manager.
- Create a new LINE Official Account.
- Click "Settings" button at the upper right corner in your LINE 
Official Account.
- Click "Messaging API" in the left menu list in "Settings".
- Click "Enable Messaging API" button.
- Select your Provider.

### Find Your Channel Access Token
- Go to the LINE Developers Console.
- Click your Provider.
- Click the Messaging API Channel in your Provider.
- Click "Messaging API" tab.
- Scroll down to find the channel access token (long-lived).
- Click "Issue" button to generate the channel access token.

### Find Your Channel Secret
- Go to the LINE Developers Console.
- Click your Provider.
- Click the Messaging API Channel in your Provider.
- Click "Basic Settings" tab.
- Scroll down to find your channel secret.

### Find Your User ID
- Go to the LINE Developers Console.
- Click your Provider.
- Click the Messaging API Channel in your Provider.
- Click "Basic Settings" tab.
- Scroll down to find your user ID.


---

## 7. How to run

### Install and Run ngrok in Raspberry Pi
- Sign up and log in to ngrok
- https://ngrok.com

- Follow the steps in the Web page
- Install ngrok
```bash
sudo snap install ngrok
```
- Add your authtoken
```bash
ngrok config add-authtoken XXXXXX
```
- Run ngrok at port 5000
```bash
ngrok http 5000
```
### Enable Webhook in Line Developers Console
- Go to the LINE Developers Console.
- Click your Provider.
- Click the Messaging API Channel in your Provider.
- Click "Messaging API" tab.
- Scroll down to find the "Webhook settings".
- Copy and paste the ngrok URL + "/callback" in the "Webhook 
URL".
- https://XXXXXX.ngrok-free.dev/callback
- Click "Verify", and then you will see "Success".
- Enable "Use webhook".

### Run the Python Program in Raspberry Pi
```bash
python app.py
```

After the system starts, it waits for the PIR sensor to detect human presence and then initiates interaction via LINE.
