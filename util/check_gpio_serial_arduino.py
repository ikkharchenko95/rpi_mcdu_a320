import RPi.GPIO as GPIO
import time

# ЖЕСТКО ФИКСИРУЕМ НАЙДЕННЫЙ ПИН!
RX_PIN = 20
BAUD_RATE = 115200

GPIO.setmode(GPIO.BCM)
GPIO.setup(RX_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Точный расчет таймингов для 115200 бод
BIT_TIME = 1.0 / BAUD_RATE  # ~8.68 микросекунд
HALF_BIT_TIME = BIT_TIME / 2.0  # Половина бита для синхронизации

print(f"✈️ [MCDU SYSTEM ONLINE] Listening on hardwired GPIO {RX_PIN}...")
print("Software-stabilized Bit-Banging UART active. Press LSK keys...\n")


def read_software_serial_byte():
    # 1. Ждем стартовый бит (падение линии в 0)
    while GPIO.input(RX_PIN) == 1:
        pass

    # 2. Идеально встаем по центру импульса
    time.sleep(HALF_BIT_TIME)

    byte_value = 0
    # 3. Считываем 8 бит данных
    for i in range(8):
        time.sleep(BIT_TIME)
        if GPIO.input(RX_PIN):
            byte_value |= (1 << i)

    # 4. Ожидаем стоповый бит
    time.sleep(BIT_TIME)

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
                # ВЫВОДИМ ЦЕЛЫЙ, СКЛЕЕННЫЙ КАДР КНОПКИ!
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
