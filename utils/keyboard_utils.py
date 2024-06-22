from sshkeyboard import listen_keyboard, stop_listening
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def listen_to_keyboard(on_press, keep_running):
    def handle_key_press(key):
        logging.debug(f"Key pressed: {key}")
        on_press(key)
        if not keep_running():
            stop_listening()
            logging.info("Keyboard listening stopped")

    listen_keyboard(on_press=handle_key_press)
