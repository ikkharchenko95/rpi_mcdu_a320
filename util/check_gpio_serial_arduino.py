import pigpio
import time

RX_PIN = 20
BAUD_RATE = 115200

pi = pigpio.pi()
if not pi.connected:
    print("[X] ОШИБКА: Запустите sudo systemctl start pigpiod")
    exit()

try:
    pi.bb_serial_read_open(RX_PIN, BAUD_RATE, 8)
    print(f"[V] UART запущен на GPIO {RX_PIN}. Ждем чистые строки...\n")
except Exception as e:
    pi.bb_serial_read_close(RX_PIN)
    pi.bb_serial_read_open(RX_PIN, BAUD_RATE, 8)

# СТРОГИЙ НАКОПИТЕЛЬНЫЙ БУФЕР
raw_accumulator = ""

try:
    while True:
        count, data = pi.bb_serial_read(RX_PIN)  # Читаем сырой поток байт [2]

        if count > 0:
            # Декодируем прилетевший кусок и намертво приклеиваем в конец накопителя [2]
            raw_accumulator += data.decode('utf-8', errors='ignore')

            # Крутим цикл, пока в накопителе есть хотя бы один символ переноса строки
            while "\n" in raw_accumulator:
                # Четко по символу \n отрезаем готовую строку от остального хвоста
                line, raw_accumulator = raw_accumulator.split("\n", 1)

                # Очищаем от мусора и пробелов
                clean_command = line.strip()

                # Выводим в консоль ТОЛЬКО полноценную, собранную строку
                if clean_command:
                    print(f"[Успешно склеенный кадр]: {clean_command}")

                    if clean_command.startswith("MCDU:LSK:"):
                        try:
                            button_info = clean_command.split(":")[-1]
                            side = "ЛЕВАЯ" if button_info[0] == 'L' else "ПРАВАЯ"
                            num = button_info[1:]
                            print(f"  [V] ОПРЕДЕЛЕНО БЕЗ ОШИБОК: Нажата {side} кнопка LSK №{num}!\n")
                        except Exception:
                            print("  [X] Строка целая, но формат поврежден")

        time.sleep(0.005)  # Чуть уменьшили паузу до 5мс для более быстрой склейки

except KeyboardInterrupt:
    pi.bb_serial_read_close(RX_PIN)
    pi.stop()
    print("\n[V] Тест завершен.")
