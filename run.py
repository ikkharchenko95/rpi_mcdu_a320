import serial
import time
from XPlaneConnectX.XPlaneConnectX import XPlaneConnectX  # нужен XPlaneConnectX в PATH
from dotenv import load_dotenv

load_dotenv()

# Arduino connection settings
SERIAL_PORT = os.getenv("SERIAL_PORT")
BAUDRATE    = os.getenv("BAUDRATE")
SERIAL_TIMEOUT = os.getenv("SERIAL_TIMEOUT")

# X‑Plane 12 settings
XPLANE_IP = os.getenv("XPLANE_IP")
XPLANE_PORT = os.getenv("XPLANE_PORT")

KEY_TO_COMMAND = {
    # INIT
    '#':  "laminar/A330/buttons/INIT",
    # CLR
    '*':  "laminar/A330/buttons/CLR",
    # 0–9, A–Z
    '0': "laminar/A330/MCDU/label_0",
    '1': "laminar/A330/MCDU/label_1",
    '2': "laminar/A330/MCDU/label_2",
    '3': "laminar/A330/MCDU/label_3",
    '4': "laminar/A330/MCDU/label_4",
    '5': "laminar/A330/MCDU/label_5",
    '6': "laminar/A330/MCDU/label_6",
    '7': "laminar/A330/MCDU/label_7",
    '8': "laminar/A330/MCDU/label_8",
    '9': "laminar/A330/MCDU/label_9",
    'A': "laminar/A330/MCDU/label_A",
    'B': "laminar/A330/MCDU/label_B",
    'C': "laminar/A330/MCDU/label_C",
    'D': "laminar/A330/MCDU/label_D",
}

# Connect to X‑Plane
xpc = XPlaneConnectX(ip=XPLANE_IP, port=XPLANE_PORT)

def send_xplane_key(key):
    cmd = KEY_TO_COMMAND.get(key, None)
    if cmd:
        xpc.sendCMND(cmd)
        print(f"[XPLANE] Sent: {key} -> {cmd}")
    else:
        print(f"[XPLANE] No such command for: {key}")

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=SERIAL_TIMEOUT)
        print(f"[INFO] Connected toArduino: {SERIAL_PORT} @ {BAUDRATE}")
        print("[INFO] Waitnig for input from MCDU A330...")

        while True:
            line = ser.readline().decode("utf-8").strip()
            if line:
                timestamp = time.strftime("%H:%M:%S")
                print(f"[{timestamp}] key: {repr(line)}")

                send_xplane_key(line)

    except serial.SerialException as e:
        print(f"[ERROR] Serial: {e}")
    except KeyboardInterrupt:
        print("\n[INFO] SIGTERM received, stop")
    finally:
        xpc.close()
        if "ser" in locals() and ser.is_open:
            ser.close()
            print("[INFO] Arduino port closed")

if __name__ == "__main__":
    main()
