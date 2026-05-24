import serial
import time
import keyboard

class ArduinoKeyReader():
    def __init__(self, on_key_pressed_callback, serial_port: str, baudrate: int=9600, timeout=1) -> None:
        if on_key_pressed_callback is None:
            raise ValueError("[ERROR] ArduinoKeyReader: on_key_pressed_callback is not set, stopping")
        self.on_key_pressed_callback = on_key_pressed_callback
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = connect()
        print(f"[INFO] Connected to Arduino: {SERIAL_PORT} @ {BAUDRATE}")
        print("[INFO] Arduino reader registered.")

    def connect():
        try:
            return serial.Serial(self.serial_port, self.baudrate, timeout=self.timeout)
        except serial.SerialException as e:
            print(f"[ERROR] Serial: {e}")
            raise e
    
    def read():
        try:
            while True:
                line = self.ser.readline().decode("utf-8").strip()
                if line:
                    print(f"[TRACE] Got line from serial port: {line}")
                    self.on_key_pressed_callback(line)

        except serial.SerialException as e:
            print(f"[ERROR] Serial: {e}")
            raise e
        except KeyboardInterrupt:
            print("[INFO] SIGTERM received, stop")
            raise e
        finally:
            xpc.close()
            if "ser" in locals() and ser.is_open:
                ser.close()
                print("[INFO] Arduino port closed")
            return