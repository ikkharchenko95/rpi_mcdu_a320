import keyboard

from reader.key_reader import KeyReader

class KeyboardKeyReader(KeyReader):
    def __init__(self, on_key_pressed_callback) -> None:
        super().__init__()
        if on_key_pressed_callback is None:
            raise ValueError("[ERROR] KeyboardKeyReader: on_key_pressed_callback is not set, stopping")

        self.on_key_pressed_callback = on_key_pressed_callback
        keyboard.on_press(self.read_keys_from_keyboard)
        print("[INFO] Keyboard reader registered.")

    def read_keys_from_keyboard(self, event):
        key_name = event.name.upper()
        print(f"[TRACE] Got key press: {event.name.upper()}")
        self.on_key_pressed_callback(key_name)