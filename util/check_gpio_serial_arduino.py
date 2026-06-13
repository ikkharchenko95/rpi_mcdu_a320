import serial
import time

# Теперь этот путь намертво зафиксирован железом на пинах 20/21
SERIAL_PORT = '/dev/ttyS0'
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
    print(f"✅ Железный UART заблокирован на {SERIAL_PORT} на скорости 115200 бод.")
    print("Ожидание нажатия LSK... (Выход: Ctrl+C)\n")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    exit()

try:
    while True:
        if ser.in_waiting > 0:
            # Железный буфер сам собирает байты со 100% точностью
            raw_data = ser.readline()
            command = raw_data.decode('utf-8', errors='ignore').strip()

            if command:
                print(f"📥 [MCDU Frame]: {command}")
                if command.startswith("MCDU:LSK:"):
                    btn_info = command.split(":")[-1]
                    side = "ЛЕВАЯ" if btn_info == 'L' else "ПРАВАЯ"
                    print(f"  🎯 УСПЕХ: Нажата {side} кнопка LSK {btn_info[1:]}!\n")

        time.sleep(0.01)

except KeyboardInterrupt:
    ser.close()
    print("\n👋 Работа завершена.")
