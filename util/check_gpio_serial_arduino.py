import RPi.GPIO as GPIO
import time

# Ваша физическая схема (пины впаяны намертво)
RX_PIN = 21  # Если при нажатии будет полная тишина, измените на 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(RX_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Точный расчет таймингов для скорости 115200 бод
BIT_TIME = 1.0 / 115200  # Длина одного бита (~8.68 микросекунд)
HALF_BIT_TIME = BIT_TIME / 2.0  # Половина бита для ловли центра импульса

print(f"✈️ [MCDU SYSTEM ONLINE] Listening on hardwired GPIO {RX_PIN}...")
print("Software-stabilized Bit-Banging UART active. Press LSK keys...\n")


def read_software_serial_byte():
    # 1. Ждем стартовый бит (когда линия падает из 1 в 0)
    while GPIO.input(RX_PIN) == 1:
        pass

    # 2. Смещаемся строго на середину стартового бита для идеальной синхронизации
    time.sleep(HALF_BIT_TIME)

    byte_value = 0
    # 3. Считываем 8 бит данных последовательно
    for i in range(8):
        time.sleep(BIT_TIME)
        if GPIO.input(RX_PIN):
            byte_value |= (1 << i)

    # 4. Ожидаем стоповый бит (возврат линии в 1)
    time.sleep(BIT_TIME)

    # Защита от мусора: если прилетел нулевой байт, игнорируем его
    if byte_value == 0 or byte_value > 127:
        return ""

    return chr(byte_value)


line_buffer = ""

try:
    while True:
        char = read_software_serial_byte()
        if not char:
            continue

        if char == '\n' or char == '\r':
            clean_command = line_buffer.strip()
            if clean_command:
                # Выводим строго и только ПОЛНОЦЕННУЮ склеенную команду
                print(f"📥 [MCDU Frame]: {clean_command}")

                if clean_command.startswith("MCDU:LSK:"):
                    btn_info = clean_command.split(":")[-1]
                    side = "LEFT" if btn_info[0] == 'L' else "RIGHT"
                    print(f"  🎯 KEY DETECTED: Side: {side} | Key: LSK {btn_info[1:]}\n")
            line_buffer = ""
        else:
            line_buffer += char

except KeyboardInterrupt:
    GPIO.cleanup()
    print("\n👋 MCDU Service stopped safely.")
