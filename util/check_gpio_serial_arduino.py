import serial
import time

SERIAL_PORT = '/dev/ttyS0'  # Hardware-locked persistent path for GPIO 20/21
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
    print(f"[V] Hardware UART locked on {SERIAL_PORT} at {BAUD_RATE} Baud.")
    print("MCDU LSK Matrix online. Awaiting keypress...\n")
except Exception as e:
    print(f"[X] Critical initialization failure: {e}")
    exit()

try:
    while True:
        if ser.in_waiting > 0:
            # Native hardware buffer handles incoming bytes instantly
            raw_data = ser.readline()
            command = raw_data.decode('utf-8', errors='ignore').strip()

            if command:
                print(f"[Frame Received]: {command}")

        time.sleep(0.01)

except KeyboardInterrupt:
    ser.close()
    print("\nMCDU Service stopped safely.")