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

## Run project

### Prerequisites

Check this file: [INSTALL.md](INSTALL.md)

Create your own .env file from .env.template file in root dir of the project, then run:

```bash
chmod +x init/init.py
```

Then just run the project:
```bash
sudo ./scripts/run.sh
```

`sudo` is needed for run because of `keyboard` lib needs root rights :(