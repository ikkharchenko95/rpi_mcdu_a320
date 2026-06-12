import pigpio
import time

# Настройки пинов (используем нумерацию BCM Broadcom, а не физические номера!)
RX_PIN = 20  # Сюда припаян провод от пина TX Arduino Nano
BAUD_RATE = 115200  # Скорость должна строго совпадать со Serial.begin в Ардуине

# Инициализируем pigpio для работы с GPIO
pi = pigpio.pi()
if not pi.connected:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: Не удалось подключиться к демону pigpio!")
    print("Запустите в терминале: sudo systemctl start pigpiod")
    exit()

# Безопасное открытие программного Serial-порта
try:
    pi.bb_serial_read_open(RX_PIN, BAUD_RATE, 8)
    print(f"✅ Программный UART успешно запущен на GPIO {RX_PIN} ({BAUD_RATE} бод).")
    print("Ожидание нажатия LSK-кнопок... (Для выхода нажмите Ctrl+C)\n")
except Exception as e:
    # Если порт был аварийно занят прошлым запуском — закрываем и открываем заново
    pi.bb_serial_read_close(RX_PIN)
    pi.bb_serial_read_open(RX_PIN, BAUD_RATE, 8)
    print(f"🔄 Порт перепущен на GPIO {RX_PIN}")

# Буфер для накопления прилетающих символов
serial_buffer = ""

try:
    while True:
        # Читаем данные из программного буфера GPIO
        # count — сколько байт прилетело, data — сами байты
        count, data = pi.bb_serial_read(RX_PIN)

        if count > 0:
            # Декодируем сырые байты в текст, игнорируя возможный мусор
            text_chunk = data.decode('utf-8', errors='ignore')
            serial_buffer += text_chunk

            # Если в буфере накопилась целая строка (заканчивается на \n)
            while "\n" in serial_buffer:
                # Отщепляем первую готовую строку от остального буфера
                line, serial_buffer = serial_buffer.split("\n", 1)

                # Удаляем невидимые символы возврата каретки (), если они есть
                command = line.strip()

                # Если строка не пустая — парсим её
                if command:
                    print(f"📥 [Сырые данные]: {command}")

                    # Проверяем, что это наша кнопка LSK
                    if command.startswith("MCDU:LSK:"):
                        # Вытаскиваем сторону (L/R) и номер кнопки
                        parts = command.split(":")
                        button_info = parts[2]  # Например, "L1" или "R5"
                        side = "ЛЕВАЯ" if button_info[0] == "L" else "ПРАВАЯ"
                        num = button_info[1]

                        print(f"  🎯 ОПРЕДЕЛЕНО: Нажата {side} кнопка LSK №{num}!\n")

        # Небольшая пауза 10 мс (100 Гц), чтобы скрипт не грузил процессор Малинки на 100%
        time.sleep(0.01)

except KeyboardInterrupt:
    # Красиво и чисто закрываем порт при нажатии Ctrl+C, чтобы пин не завис
    print("\nЗавершение работы...")
    pi.bb_serial_read_close(RX_PIN)
    pi.stop()
    print("👋 Программный UART успешно закрыт. Всего доброго!")
