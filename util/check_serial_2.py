import pigpio
import time

pi = pigpio.pi()
if not pi.connected:
    exit()

# Открываем программный TX на пине 20 и RX на пине 21
try:
    pi.bb_serial_read_open(21, 115200, 8)
except:
    pi.bb_serial_read_close(21)
    pi.bb_serial_read_open(21, 115200, 8)

print("📡 Тест эхо-петли запущен. Отправляем тестовый пакет...")

# Плюем тестовую строчку в пин 20
pi.wave_clear()
pi.wave_add_serial(20, 115200, "MCDU:TEST\n")
wave_id = pi.wave_create()
pi.wave_send_once(wave_id)

# Ждем долю секунды, пока сигнал пробежит по скрепке из пина 20 в пин 21
time.sleep(0.1)

# Читаем то, что прилетело в пин 21
count, data = pi.bb_serial_read(21)

if count > 0:
    print(f"✅ УСПЕХ! Малинка услышала сама себя: {data.decode('utf-8').strip()}")
    print("Это значит: Пины GPIO 20/21 абсолютно живы, и софт Linux работает идеально.")
else:
    print("❌ ТИШИНА. Малинка сама себя не слышит.")
    print("Это значит: пины сгорели, либо pigpiod завис.")

pi.bb_serial_read_close(21)
pi.stop()