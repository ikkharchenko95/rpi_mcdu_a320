import pigpio
import time
import threading
import logging

logger = logging.getLogger(__name__)

from reader.key_reader import KeyReader

class ArduinoKeyReader(KeyReader):
    def __init__(self, on_key_pressed_callback, rx_pin: int, baudrate: int = 9600) -> None:
        super().__init__()
        if on_key_pressed_callback is None:
            raise ValueError("[ERROR] ArduinoKeyReader: on_key_pressed_callback is not set, stopping")

        self.on_key_pressed_callback = on_key_pressed_callback
        self.rx_pin = rx_pin
        self.baudrate = baudrate

        self.pi = pigpio.pi()
        self.line_accumulator = ""
        self.is_running = False
        self.is_port_opened = False
        self._thread = None

        if not self.pi.connected:
            logger.error("Arduino reader: Could not connect to pigpiod! Is there a service running?")
            raise RuntimeError("pigpiod daemon is not running")

        logger.info("Arduino reader registered.")

    def start(self):
        self.is_running = True
        self._try_open_port()

        self._thread = threading.Thread(target=self._read_loop, daemon=True, name="MCDU-SerialReader")
        self._thread.start()
        logger.info(f"Arduino reader: thread started.")

    def _try_open_port(self):
        try:
            self.pi.bb_serial_read_close(self.rx_pin)
        except Exception:
            pass

        try:
            res = self.pi.bb_serial_read_open(self.rx_pin, self.baudrate, 8)
            if res >= 0:
                self.is_port_opened = True
                logger.info(f"Arduino reader reader: GPIO port {self.rx_pin} opened on {self.baudrate} baud.")
                return True
            else:
                self.is_port_opened = False
                logger.error(f"Arduino reader: pigpio error during open port: {res}")
                return False
        except Exception as e:
            self.is_port_opened = False
            logger.error(f"Arduino reader: exception during open port: {e}")
            return False

    def _read_loop(self):
        while self.is_running:
            if not self.is_port_opened:
                logger.warning("Arduino reader: connection lost, reconnecting in 2 seconds...")
                time.sleep(2.0)
                if self._try_open_port():
                    self.line_accumulator = ""
                continue

            try:
                count, data = self.pi.bb_serial_read(self.rx_pin)

                if count < 0:
                    logger.error(f"Arduino reader: Hardware fault during read data (code {count}). Try to reconnect.")
                    self.is_port_opened = False
                    continue

                if count > 0:
                    self.line_accumulator += data.decode('utf-8', errors='ignore')

                    while "\n" in self.line_accumulator:
                        line, self.line_accumulator = self.line_accumulator.split("\n", 1)
                        clean_cmd = line.strip()

                        if clean_cmd:
                            logger.debug(f"Arduino reader: got frame {clean_cmd}")

                            if self.on_key_pressed_callback:
                                try:
                                    self.on_key_pressed_callback(clean_cmd)
                                except Exception as callback_err:
                                    logger.error(f"Arduino reader: Error on on_key_pressed_callback: {callback_err}")

            except Exception as e:
                logger.error(f"⚠Arduino reader: Critical exception on read: {e}. Restarting...")
                self.is_port_opened = False

            # Pause 8 ms for release Raspberry processor
            time.sleep(0.008)

    def stop(self):
        self.is_running = False
        self.is_port_opened = False
        if self._thread:
            self._thread.join(timeout=1)
        if self.pi and self.pi.connected:
            try:
                self.pi.bb_serial_read_close(self.rx_pin)
            except Exception:
                pass
            self.pi.stop()
        logger.info("Arduino reader: read and autoconnect thread successfully stopped.")
