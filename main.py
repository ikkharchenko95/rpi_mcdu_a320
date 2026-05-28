import os
import time
import threading
from dotenv import load_dotenv

from adapter.sim.impl.xplane_adapter import XPlaneAdapter

from reader.impl.arduino_key_reader import ArduinoKeyReader
from reader.impl.keyboard_key_reader import KeyboardKeyReader

from mapping.mcdu_mapping import McduMapping

load_dotenv()

def init_envs() -> dict:
    return {
        "ARDUINO_SERIAL_PORT": os.getenv("ARDUINO_SERIAL_PORT"),
        "ARDUINO_BAUDRATE": int(os.getenv("ARDUINO_BAUDRATE")),
        "ARDUINO_SERIAL_TIMEOUT": int(os.getenv("ARDUINO_SERIAL_TIMEOUT")),
        "MCDU_TYPE": int(os.getenv("MCDU_TYPE")),
        "XPLANE_IP": os.getenv("XPLANE_IP"),
        "XPLANE_PORT": int(os.getenv("XPLANE_PORT")),
    }

def main():

    # Init envs
    envs = init_envs()

    xpc = None
    try:
        # Get MCDU mapping
        mcdu_mapping = McduMapping(envs["MCDU_TYPE"])

        # Connect to X‑Plane
        xpc = XPlaneAdapter(xplane_ip=envs["XPLANE_IP"],
                            xplane_port=envs["XPLANE_PORT"],
                            mcdu_mapping=mcdu_mapping)

        # Init Arduino key reader
        lsk_keys_reader = ArduinoKeyReader(
            on_key_pressed_callback=xpc.send_command,
            ARDUINO_SERIAL_PORT=envs["ARDUINO_SERIAL_PORT"],
            ARDUINO_BAUDRATE=envs["ARDUINO_BAUDRATE"],
            timeout=envs["ARDUINO_SERIAL_TIMEOUT"]
        )
        lsk_keys_reader_thread = threading.Thread(target=lsk_keys_reader.read,
                                                  daemon=True)
        lsk_keys_reader_thread.start()

        # Init keyboard key reader
        keyboard_keys_reader = KeyboardKeyReader(
            on_key_pressed_callback=xpc.send_command
        )

        print("[INFO] Waiting for input from MCDU A330...")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[INFO] Exiting application gracefully...")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        if None is not xpc:
            xpc.close()


if __name__ == "__main__":
    main()
