import time
import threading

import serial

from reader.key_reader import KeyReader

class ArduinoKeyReader(KeyReader):
    def __init__(self, on_key_pressed_callback, ARDUINO_SERIAL_PORT: str, ARDUINO_BAUDRATE: int = 9600, timeout=1) -> None:
        super().__init__()
        if on_key_pressed_callback is None:
            raise ValueError("[ERROR] ArduinoKeyReader: on_key_pressed_callback is not set, stopping")
        self.on_key_pressed_callback = on_key_pressed_callback
        self.ARDUINO_SERIAL_PORT = ARDUINO_SERIAL_PORT
        self.ARDUINO_BAUDRATE = ARDUINO_BAUDRATE
        self.timeout = timeout
        self.ser = self.connect()
        print(f"[INFO] Connected to Arduino: {ARDUINO_SERIAL_PORT} @ {ARDUINO_BAUDRATE}")
        print("[INFO] Arduino reader registered.")

    def __del__(self):
        print(f"[INFO] Arduino serial port closed")
        self.ser.close()

    def connect(self):
        try:
            return serial.Serial(self.ARDUINO_SERIAL_PORT, self.ARDUINO_BAUDRATE, timeout=self.timeout)
        except serial.SerialException as e:
            print(f"[ERROR] Serial: {e}")
            self.on_disconnect()
            raise e
    
    def read(self):
        try:
            while True:
                line = self.ser.readline().decode("utf-8").strip()
                if line:
                    print(f"[TRACE] Got line from serial port: {line}")
                    self.on_key_pressed_callback(line)

        except serial.SerialException as e:
            print(f"[ERROR] Serial: {e}")
            raise e
        except KeyboardInterrupt as e:
            print("[INFO] SIGTERM received, stop")
            raise e
        finally:
            if "ser" in locals() and self.ser.is_open:
                self.ser.close()
                print("[INFO] Arduino port closed")
            return

    def on_disconnect(self):
        print("[ERROR] Arduino disconnected, trying to reconnect in 3 seconds...")
        self.try_to_connect()

    def try_to_connect(self):
        time.sleep(3)
        thread = threading.Thread(target=self.connect)
        thread.start()