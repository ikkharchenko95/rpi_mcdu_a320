# rpi_mcdu_a320
MCDU for Airbus A320 (XPlane 12). Uses Arduino Uno R3 for read keys from physical keyboard, and Raspberry Pi 3B as a server.

## Instruments

Tested on:
- Raspberry Pi 3B
- Arduino Uno R3
- Bluetooth keyboard with touchpad

For input information to MCDU, 
I just use the simple Bluetooth keyboard for process input A-Z, 0-9, 
some special chars (/, +-, etc.) and F1-F12 as a functional buttons (DIR, PERF etc.).  
For process input from LSK keys, I use two circuit boards with 12 tact buttons: 6 from each side. 

## Init
1. Run:
```bash
chmod +x init/init.py
init/init.py
```

2. Choose the device you want to use as an Arduino (for process LSK keys)

## If you don't want to run init

1. Manually run

```bash
lsusb -l
```

2. Get serial uid of your device

3. Manually add `ARDUINO_SERIAL_PORT` env variable.


## Run project

Create your own .env file from .env.template file in root dir of the project, then run:

```bash
chmod +x init/init.py
```

Then just run the project:
```bash
python3 main.py .env
```