import os
import time
from dotenv import load_dotenv
from xplane_connect import XPlaneConnectX

from arduino_key_reader import ArduinoKeyReader
from keyboard_key_reader import KeyboardKeyReader

from mcdu_mapping import McduMapping

load_dotenv()

KEY_TO_COMMAND = {}

def send_xplane_key(key):
    global KEY_TO_COMMAND
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] key: {repr(key)}")

    print(f"{KEY_TO_COMMAND}")

    cmd = KEY_TO_COMMAND.get(key, None)
    if cmd:
        xpc.sendCMND(cmd)
        print(f"[XPLANE] Sent: {key} -> {cmd}")
    else:
        print(f"[XPLANE] No such command for: {key}")


def init_envs() -> dict:
    return {
        "SERIAL_PORT": os.getenv("SERIAL_PORT"),
        "BAUDRATE": int(os.getenv("BAUDRATE")),
        "SERIAL_TIMEOUT": int(os.getenv("SERIAL_TIMEOUT")),
        "MCDU_TYPE": int(os.getenv("MCDU_TYPE")),
        "XPLANE_IP": os.getenv("XPLANE_IP"),
        "XPLANE_PORT": int(os.getenv("XPLANE_PORT")),
    }

def main():

    # Init envs
    envs = init_envs()

    # Connect to X‑Plane
    xpc = XPlaneConnectX(ip=envs["XPLANE_IP"], port=envs["XPLANE_PORT"])

    try:
        global KEY_TO_COMMAND
        # Get MCDU mapping
        mcdu_mapping = McduMapping(envs["MCDU_TYPE"])
        KEY_TO_COMMAND = mcdu_mapping.get_mapping()
    except Exception as e:
        xpc.close()
        print(f"[ERROR] Cannot read MCDU mappings from json config: {e}")
        return

    try:
        lsk_keys_reader = ArduinoKeyReader(
            on_key_pressed_callback=send_xplane_key, 
            serial_port=envs["SERIAL_PORT"],
            baudrate=envs["BAUDRATE"],
            timeout=envs["SERIAL_TIMEOUT"]
        )
        lsk_keys_reader.read()

        keyboard_keys_reader = KeyboardKeyReader(
            on_key_pressed_callback=send_xplane_key
        )

        print("[INFO] Waiting for input from MCDU A330...")
    except Exception as e:
        if type(e) is not KeyboardInterrupt:
            print(f"[ERROR] Error: {e}")
        xpc.close()


if __name__ == "__main__":
    main()
