import RPi.GPIO as GPIO
import time

# Настройка пинов (Используем нумерацию BCM)
RX_PIN = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(RX_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print(f"📡 Высокоточный обработчик RPi.GPIO запущен на GPIO {RX_PIN}...")
print("Слушаем нажатия LSK на скорости 115200 бод... (Выход: Ctrl+C)\n")

# Математика таймингов для скорости 115200 бод
# Длина одного бита в секундах = 1 / 115200
BIT_TIME = 1.0 / 115200
HALF_BIT_TIME = BIT_TIME / 2.0


def read_hardware_byte():
    # Ожидаем стартовый бит (падение пина в 0)
    while GPIO.input(RX_PIN) == 1:
        pass

    # Ждем до середины стартового бита для синхронизации
    time.sleep(HALF_BIT_TIME)

    byte_value = 0
    # Считываем 8 бит данных
    for i in range(8):
        time.sleep(BIT_TIME)
        if GPIO.input(RX_PIN):
            byte_value |= (1 << i)

    # Ждем стоповый бит
    time.sleep(BIT_TIME)
    return chr(byte_value)


buffer = ""

try:
    while True:
        # Ловим символ напрямую из кремния
        char = read_hardware_byte()

        if char == '\n':
            clean_cmd = buffer.strip()
            if clean_cmd:
                print(f"📥 [Чистый кадр LSK]: {clean_cmd}")
                if clean_cmd.startswith("MCDU:LSK:"):
                    btn = clean_cmd.split(":")[-1]
                    side = "ЛЕВАЯ" if btn[0] == 'L' else "ПРАВАЯ"
                    print(f"  🎯 УСПЕХ: Нажата {side} кнопка №{btn[1:]}!\n")
            buffer = ""
        else:
            buffer += char

except KeyboardInterrupt:
    GPIO.cleanup()
    print("\n👋 Служба MCDU остановлена.")
