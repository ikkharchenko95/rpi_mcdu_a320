import RPi.GPIO as GPIO
import time

# Ваш жестко впаянный рабочий пин
RX_PIN = 20
BAUD_RATE = 115200

GPIO.setmode(GPIO.BCM)
GPIO.setup(RX_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Рассчитываем микросекундные тайминги для 115200 бод
BIT_TIME = 1.0 / BAUD_RATE  # ~8.68 микросекунд
HALF_BIT_TIME = BIT_TIME / 2.0

print(f"✈️ [MCDU HARDWARE ACTIVE] Listening on hardwired GPIO {RX_PIN}...")
print("Oversampled Software UART online. Press LSK keys...\n")


def read_stable_byte():
    # 1. Ожидаем падения линии в 0 (Стартовый бит)
    while GPIO.input(RX_PIN) == 1:
        pass

    # 2. Смещаемся на середину импульса для синхронизации
    time.sleep(HALF_BIT_TIME)

    byte_value = 0
    # 3. Читаем 8 бит данных последовательно
    for i in range(8):
        time.sleep(BIT_TIME)

        # ФИЛЬТР: делаем 3 быстрых микро-опроса пина, чтобы исключить лаг Linux
        sample1 = GPIO.input(RX_PIN)
        sample2 = GPIO.input(RX_PIN)
        sample3 = GPIO.input(RX_PIN)

        # Мажоритарный выбор: бит равен 1, только если хотя бы 2 опроса из 3 дали единицу
        bit = 1 if (sample1 + sample2 + sample3) >= 2 else 0

        if bit:
            byte_value |= (1 << i)

    # 4. Ожидаем завершения стопового бита
    time.sleep(BIT_TIME)

    # Защита от мусора и пустых байт
    if byte_value == 0 or byte_value > 127:
        return ""

    return chr(byte_value)


line_buffer = ""

try:
    while True:
        char = read_stable_byte()
        if not char:
            continue

        if char == '\n' or char == '\r':
            clean_command = line_buffer.strip()
            if clean_command:
                # ВЫВОДИМ СТРОГО ЦЕЛУЮ, СКЛЕЕННУЮ СТРОКУ КНОПКИ
                print(f"📥 [MCDU Frame]: {clean_command}")

                if clean_command.startswith("MCDU:LSK:"):
                    btn_info = clean_command.split(":")[-1]
                    side = "LEFT" if btn_info.startswith('L') else "RIGHT"
                    print(f"  🎯 KEY DETECTED: Side: {side} | Key: LSK {btn_info[1:]}\n")
            line_buffer = ""
        else:
            line_buffer += char

except KeyboardInterrupt:
    GPIO.cleanup()
    print("\n👋 MCDU Service stopped safely.")
