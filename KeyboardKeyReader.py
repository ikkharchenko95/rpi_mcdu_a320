import keyboard

class KeyboardKeyReader():
    def __init__(self, on_key_pressed_callback) -> None:
        if on_key_pressed_callback is None:
            raise ValueError("[ERROR] KeyboardKeyReader: on_key_pressed_callback is not set, stopping")

        keyboard.on_press(read_keys_from_keyboard)
        keyboard.wait()
        print("[INFO] Keyboard reader registered.")

    def read_keys_from_keyboard(event):
        # Check if the pressed key is a Function key (F1-F12)
        key_name = event.name.upper()
        print(f"[TRACE] Got key press: {event.name.upper()}")
        self.on_key_pressed_callback(key_name)