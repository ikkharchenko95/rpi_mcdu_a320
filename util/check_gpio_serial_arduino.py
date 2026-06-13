import serial
import time

try:
    ser = serial.Serial(
        port='/dev/ttyS0',
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )
    print("✅ Железный UART Малинки успешно активирован на 115200 бод.")
    print("Ожидание нажатия LSK... (Для выхода Ctrl+C)\n")
except Exception as e:
    print(f"❌ ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
    print("Возможно, порт занят консолью Linux. Напишите мне, если выскочит эта ошибка.")
    exit()

try:
    while True:
        # Железный метод readline() ждет, пока в буфер не прилетит честный \n от Ардуины
        if ser.in_waiting > 0:
            raw_bytes = ser.readline()

            # Декодируем и очищаем строку
            clean_command = raw_bytes.decode('utf-8', errors='ignore').strip()

            if clean_command:
                print(f"📥 [Чистый кадр]: {clean_command}")

                if clean_command.startswith("MCDU:LSK:"):
                    button_info = clean_command.split(":")[-1]
                    side = "ЛЕВАЯ" if button_info[0] == 'L' else "ПРАВАЯ"
                    num = button_info[1:]
                    print(f"  🎯 УСПЕХ: Нажата {side} кнопка LSK №{num}!\n")

        time.sleep(0.01)

except KeyboardInterrupt:
    ser.close()
    print("\n👋 Тест завершен.")
