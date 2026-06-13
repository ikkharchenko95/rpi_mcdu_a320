# Check serial on GPIO ports in Raspberry

## pigpiod installation

```bash
sudo apt-get update
sudo apt-get install -y python3-setuptools python3-full wget make gcc

wget https://github.com/joan2937/pigpio/archive/refs/tags/v79.tar.gz
tar zxf v79.tar.gz
cd pigpio-79; make; sudo make install

sudo ldconfig
sudo systemctl daemon-reload
sudo systemctl enable --now pigpiod

sudo systemctl status pigpiod
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

### Step 2: Route Hardware UART to GPIO 20 & 21
Since native hardware serial lines do not sit on pins 20/21 by default, we use a device tree overlay to re-route the hardware rails on a silicon level.

1. Open the main system configuration file:
   ```bash
   sudo nano /boot/firmware/config.txt
   ```
   *(On older legacy OS versions, use: `sudo nano /boot/config.txt`)*

2. Scroll to the very bottom of the file and append the following lines:
   ```text
   # Route hardware Mini-UART to MCDU data pins
   dtoverlay=uart2,tx0_pin=20,rx0_pin=21
   enable_uart=1
   ```
3. Save the file (`Ctrl + O`, then `Enter`) and exit (`Ctrl + X`).

### Step 3: Apply Changes and Reboot
Restart the Raspberry Pi to let the Linux kernel switch the physical routing matrix:
```bash
sudo reboot
```

---

## 🛡️ Device Persistence Warning (USB vs. GPIO)

* **Why this setup is bulletproof:** Unlike external USB devices which dynamically change names after rebooting (e.g., drifting randomly between `/dev/ttyUSB0` and `/dev/ttyUSB1`), internal GPIO serial controllers are mapped to static hardware registers.
* **The Result:** The device path **`/dev/ttyS0`** is tied permanently to **GPIO 20/21** on a hardware level. It will never drift or change names, eliminating the need for complex `udev` rules or `/dev/serial/by-id/` symbolic links.

---

## 🐍 Python 3 Implementation Template

Install the stable hardware serial wrapper:
```bash
pip3 install pyserial --break-system-packages
```

Run the following background listener (`mcdu_listener.py`):

```python
import serial
import time

SERIAL_PORT = '/dev/ttyS0' # Hardware-locked persistent path for GPIO 20/21
BAUD_RATE = 115200

try:
    ser = serial.Serial(
        port=SERIAL_PORT,
        baudrate=BAUD_RATE,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )
    print(f"✅ Hardware UART locked on {SERIAL_PORT} at {BAUD_RATE} Baud.")
    print("🤖 MCDU LSK Matrix online. Awaiting keypress...\n")
except Exception as e:
    print(f"❌ Critical initialization failure: {e}")
    exit()

try:
    while True:
        if ser.in_waiting > 0:
            # Native hardware buffer handles incoming bytes instantly
            raw_data = ser.readline()
            command = raw_data.decode('utf-8', errors='ignore').strip()
            
            if command and command.startswith("MCDU:LSK:"):
                print(f"📥 [Frame Received]: {command}")
                # Add your custom flight-sim event triggers here
                
        time.sleep(0.01)

except KeyboardInterrupt:
    ser.close()
    print("\n👋 MCDU Service stopped safely.")
```
