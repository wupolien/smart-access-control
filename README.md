# 智慧門禁系統  Smart Access Control System

本專題為一套以樹莓派（Raspberry Pi）為核心之智慧門禁系統，整合 PIR 人體紅外線感測器、LCD 顯示模組、伺服馬達、LED 指示燈、蜂鳴器以及 LINE Messaging API，即時通訊機制。系統可於偵測到人員接近時自動啟動驗證流程，並透過 LINE 平台進行密碼驗證與即時通知。

This project presents a Raspberry Pi–based smart access control system integrating a PIR sensor, LCD display, servo motor, LEDs, buzzer, and the LINE Messaging API. The system automatically initiates authentication when human presence is detected and provides real-time feedback and notifications via LINE.

---

## 一、系統功能  System Features

- PIR 人體感測器自動偵測人員靠近  / Automatic human detection using PIR sensor 
- LCD 顯示提示訊息（Password Please）  / LCD displays system prompts  
- 使用者可透過 LINE 輸入密碼進行驗證  / Password authentication via LINE Messaging API  
- 驗證成功：伺服馬達開門、綠色 LED 亮起、LINE 通知  / Successful authentication triggers door opening and notification
- 驗證失敗：紅色 LED 與蜂鳴器警示、LINE 通知  / Failed authentication triggers alarm and warning notification 

---

## 二、系統架構  System Architecture

本系統採用分層式架構設計，分為感測層、控制層與通訊層。/ The system architecture consists of three layers:

- **感測層（Sensing Layer）**：PIR 人體紅外線感測器  / PIR motion sensor 
- **控制層（Control Layer）**：Raspberry Pi（Python）  
- **通訊層（Communication Layer）**：LINE Messaging API（Webhook + HTTP）  

---

## 三、硬體需求  Hardware Requirements

- Raspberry Pi  
- PIR 人體紅外線感測器 (PIR Motion Sensor)  
- LCD 1602 顯示模組（I2C）  
- SG90 伺服馬達 (Servo Motor)  
- LED（紅色 / 綠色）  
- 蜂鳴器 (Buzzer)  
- 外接 5V 電源（建議供給馬達）  

---

## 四、硬體接線說明  Hardware Wiring (GPIO Configuration)

### GPIO 腳位對應表  GPIO Pin Mapping

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

### 注意事項  Notes

- 伺服馬達需使用外接電源，避免因電壓不足導致異常轉動。  / Use an external power supply for the servo motor.  
- LED 必須串接限流電阻以保護 GPIO 腳位。  / LEDs must be connected with current-limiting resistors. 
- 所有模組需共地（GND 共用）以確保訊號穩定。  / Ensure all modules share a common ground (GND).  

---

## 五、軟體需求  Software Requirements

- Python 3.9 or above  
- Flask  
- gpiozero  
- python-dotenv  
- line-bot-sdk  

安裝套件 / Install dependencies:

```bash
pip install -r requirements.txt
```
---

## 六、環境設定 Environment settings

請建立 `.env` 檔案，內容如下：

```env
LINE_CHANNEL_ACCESS_TOKEN=你的TOKEN
LINE_CHANNEL_SECRET=你的SECRET
PORT=5000
```

---

## 六、執行方式

```bash
python app.py
```

啟動後，系統將等待 PIR 偵測人員接近並透過 LINE 進行互動。
