import pigpio
import time

# НАСТРОЙКА: Пин 20 (который мы нашли), скорость подбираем под Ардуину
RX_PIN = 20
BAUD_RATE = 9600

pi = pigpio.pi()
if not pi.connected:
    print("❌ Запустите sudo ./pigpiod")
    exit()

# Безопасное открытие
try:
    pi.bb_serial_read_close(RX_PIN)
except:
    pass

try:
    pi.bb_serial_read_open(RX_PIN, BAUD_RATE, 8)
    print(f"🚀 UART открыт на GPIO {RX_PIN} со скоростью {BAUD_RATE} бод.")
    print("Нажимайте LSK... (Выход: Ctrl+C)\n")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    exit()

# Бронированный накопитель
line_accumulator = ""

try:
    while True:
        count, data = pi.bb_serial_read(RX_PIN)

        if count > 0:
            line_accumulator += data.decode('utf-8', errors='ignore')

            while "\n" in line_accumulator:
                line, line_accumulator = line_accumulator.split("\n", 1)
                clean_cmd = line.strip()

                if clean_cmd:
                    # Выводим СЫРУЮ строку, чтобы видеть, пропадает ли мусор
                    print(f"📥 [Принято]: {clean_cmd}")

                    if clean_cmd.startswith("MCDU:LSK:"):
                        print("  🎯 СТРОКА ИДЕАЛЬНО СКЛЕЕНА БЕЗ МУСОРА!")

        time.sleep(0.01)

except KeyboardInterrupt:
    pi.bb_serial_read_close(RX_PIN)
    pi.stop()
