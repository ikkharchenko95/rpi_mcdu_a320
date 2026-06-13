import serial
import time

# Железный путь для оверлея uart2 на Raspberry Pi 3B
SERIAL_PORT = '/dev/ttyAMA1'
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
    print(f"✅ Железный UART0 успешно заперт на {SERIAL_PORT} на скорости {BAUD_RATE} бод.")
    print("Ожидание нажатия LSK... (Выход: Ctrl+C)\n")
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    print("Если вылезла ошибка, попробуйте изменить порт на '/dev/serial1'")
    exit()

try:
    while True:
        if ser.in_waiting > 0:
            # Железный буфер сам склеит пакеты по символу \n
            raw_data = ser.readline()
            command = raw_data.decode('utf-8', errors='ignore').strip()

            if command:
                print(f"📥 [MCDU Frame]: {command}")
                if command.startswith("MCDU:LSK:"):
                    btn_info = command.split(":")[-1]
                    side = "ЛЕВАЯ" if btn_info.startswith('L') else "ПРАВАЯ"
                    print(f"  🎯 УСПЕХ: Нажата {side} кнопка LSK {btn_info[1:]}!\n")

        time.sleep(0.01)

except KeyboardInterrupt:
    ser.close()
    print("\n👋 Работа завершена.")
