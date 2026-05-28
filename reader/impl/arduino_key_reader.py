import time

import serial

from reader.key_reader import KeyReader

class ArduinoKeyReader(KeyReader):
    def __init__(self, on_key_pressed_callback, serial_port: str, baudrate: int = 9600, timeout=1) -> None:
        super().__init__()
        if on_key_pressed_callback is None:
            raise ValueError("[ERROR] ArduinoKeyReader: on_key_pressed_callback is not set, stopping")

        self.on_key_pressed_callback = on_key_pressed_callback
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout

        self.is_running = True
        self.ser = None

        self.connect()
        print("[INFO] Arduino reader registered.")

    def connect(self):
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()

            self.ser = serial.Serial(self.serial_port, self.baudrate, timeout=self.timeout)
            print(f"[INFO] Connected to Arduino: {self.serial_port} @ {self.baudrate}")
            return True
        except serial.SerialException as e:
            print(f"[ERROR] Serial connection failed: {e}")
            self.ser = None
            return False
    
    def read(self):
        print("[INFO] Start reading loop...")
        while self.is_running:
            # If port is closed - then reconnect
            if self.ser is None or not self.ser.is_open:
                self.on_disconnect()
                continue

            try:
                line = self.ser.readline().decode("utf-8").strip()
                if line:
                    print(f"[TRACE] Got line from serial port: {line}")
                    self.on_key_pressed_callback(line)

            except (serial.SerialException, OSError) as e:
                print(f"[ERROR] Serial error during read: {e}")
                if self.ser:
                    try:
                        self.ser.close()
                    except Exception:
                        pass
                self.ser = None

            except KeyboardInterrupt:
                print("[INFO] SIGTERM received, stop")
                self.is_running = False
                break

        # Close port
        if self.ser and self.ser.is_open:
            self.ser.close()

    def on_disconnect(self):
        print("[ERROR] Arduino disconnected, trying to reconnect in 3 seconds...")
        time.sleep(3)
        self.connect()
