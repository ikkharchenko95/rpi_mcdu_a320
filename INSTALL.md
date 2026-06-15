# Installation

## pigpiod dependency installation as a system service

```bash
sudo apt-get update &&\
 sudo apt-get install -y python3-setuptools python3-full wget make gcc &&\
 wget https://github.com/joan2937/pigpio/archive/refs/tags/v79.tar.gz &&\
 tar zxf v79.tar.gz &&\
 cd pigpio-79 && make && sudo make install &&\
 sudo cp /home/user/pigpio-79 /opt/pigpio &&\
 sudo ldconfig &&\
 sudo vim /etc/systemd/system/pigpiod.service
```

Add this unit:
```
[Unit]
Description=Pigpio daemon for GPIO control
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/bin/pigpiod
ExecStop=/bin/killall pigpiod
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then
```bash
sudo systemctl daemon-reload &&\
  sudo systemctl enable --now pigpiod &&\
  sudo systemctl status pigpiod

```

## Project installation as a system service
```bash
git clone https://github.com/ikkharchenko95/rpi_mcdu_a320.git &&\
  sudo cp rpi_mcdu_a320 /opt/rpi_mcdu_a320 &&\
  sudo cp /opt/rpi_mcdu_a320/.env.template /opt/rpi_mcdu_a320/.env &&\
  sudo apt-get install -y python3-venv &&\
  python3 -m venv venv &&\
  source venv/bin/activate &&\
  pip install -r requirements.txt &&\
  sudo chmod +x ./scripts/run.sh &&\
  sudo chown -R $USER:$USER ./scripts/run.sh &&\
  sudo vim /etc/systemd/system/mcdu_a320.service
```

Add this unit (don't forget to change your username):
```
[Unit]
Description=MCDU Airbus A320 Flight Sim Board Service
After=pigpiod.service

[Service]
Type=simple
User=%YOUR_USERNAME%
WorkingDirectory=/opt/rpi_mcdu_a320
ExecStart=/bin/bash /opt/rpi_mcdu_a320/scripts/run.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then enable and start service:
```bash
sudo systemctl daemon-reload &&\
 sudo systemctl enable --now mcdu_a320.service &&\
 sudo systemctl start mcdu_a320.service
```

# ✈️ MCDU Interface Board Setup Guide

This guide describes how to configure the Raspberry Pi 3B hardware UART pins to communicate with the Arduino Nano (LSK Button Matrix) at **115200 Baud** without data corruption, ghost characters, or device name drifting.

---

## 📌 Hardware Pin Mapping

To avoid software-emulated serial jitter (caused by `pigpio` bit-banging), we map the native Raspberry Pi hardware **Mini-UART** controller directly to the custom GPIO pins used in this build.

| Signal | Arduino Nano Pin | Raspberry Pi 3B Pin | Physical Pin # |
| :--- | :---: | :---: | :---: |
| **+5V Power** | 5V | 5V Power | Pin 2 or 4 |
| **Ground** | GND | GND | Pin 30, 34, or 39 |
| **TX (Transmit)** | TX (TX1) | **GPIO 21 (RX)** | **Pin 40** |
| **RX (Receive)** | RX (RX0) | **GPIO 20 (TX)** | **Pin 38** |

> ⚠️ **Note:** Data lines must be crossed (`TX` ➡️ `RX` and `RX` ➡️ `TX`).

---

## 🛠️ Step-by-Step Configuration

### Step 1: Free the Hardware UART from Linux OS Kernel
By default, Linux uses the hardware serial port to stream system boot logs and provide a login shell. We must disable this to prevent garbage data from entering our Python script.

1. Open the Raspberry Pi configuration utility:
   ```bash
   sudo raspi-config
   ```
2. Navigate to: **Interface Options** ➡️ **Serial Port**.
3. When asked: *Would you like a login shell to be accessible over the serial?* ➡️ Select **No**.
4. When asked: *Would you like the serial port hardware to be enabled?* ➡️ Select **Yes**.
5. Select **Finish** and choose **No** when asked to reboot (we will reboot after Step 2).

