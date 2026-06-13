import RPi.GPIO as GPIO
import time

# Заставляем скрипт слушать СРАЗУ ОБА возможных пина!
PINS = [20, 21]

GPIO.setmode(GPIO.BCM)
for pin in PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

BIT_TIME = 1.0 / 115200  # Длина одного бита (~8.68 мкс)
HALF_BIT_TIME = BIT_TIME / 2.0  # Половина бита для ловли центра

print("✈️ [MCDU AUTODETECT ONLINE] Listening on BOTH GPIO 20 and GPIO 21...")
print("Press any LSK key to detect the correct data wire...\n")


def read_byte_from_pin(active_pin):
    # Смещаемся на середину стартового бита для идеальной синхронизации
    time.sleep(HALF_BIT_TIME)

    byte_value = 0
    for i in range(8):
        time.sleep(BIT_TIME)
        if GPIO.input(active_pin):
            byte_value |= (1 << i)

    time.sleep(BIT_TIME)  # Ожидаем стоп-бит

    if byte_value == 0 or byte_value > 127:
        return ""
    return chr(byte_value)


line_buffer = ""
active_rx_pin = None

try:
    while True:
        # 1. Если рабочий пин еще не определен, сканируем оба в реальном времени
        if active_rx_pin is None:
            for pin in PINS:
                if GPIO.input(pin) == 0:  # Поймали падение линии (стартовый бит)!
                    active_rx_pin = pin
                    print(f"🎯 АВТООПРЕДЕЛЕНИЕ: Сигнал от Ардуины успешно найден на GPIO {active_rx_pin}!")
                    break
            if active_rx_pin is None:
                time.sleep(0.001)  # Микропауза для разгрузки процессора
                continue

        # 2. Читаем байт с уже определенного рабочего пина
        char = read_byte_from_pin(active_rx_pin)

        # Если прилетел мусор из-за дребезга в момент первого захвата, сбрасываем пин на перепроверку
        if not char:
            active_rx_pin = None
            continue

        if char == '\n' or char == '\r':
            clean_command = line_buffer.strip()
            if clean_command:
                print(f"📥 [MCDU Frame via GPIO {active_rx_pin}]: {clean_command}")
                if clean_command.startswith("MCDU:LSK:"):
                    btn_info = clean_command.split(":")[-1]
                    side = "LEFT" if btn_info == 'L' else "RIGHT"
                    print(f"  🎯 KEY DETECTED: Side: {side} | Key: LSK {btn_info[1:]}\n")
            line_buffer = ""
            active_rx_pin = None  # Возвращаемся в режим сканирования для следующей кнопки
        else:
            line_buffer += char

except KeyboardInterrupt:
    GPIO.cleanup()
    print("\n👋 MCDU Service stopped safely.")
