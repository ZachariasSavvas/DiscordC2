import sys
import subprocess

def list_services():
    """Return a formatted list of services and their states."""
    try:
        if sys.platform.startswith('win'):
            result = subprocess.check_output(['sc', 'query', 'type=', 'service', 'state=', 'all'], text=True)
            return result
        else:
            result = subprocess.check_output(['systemctl', 'list-units', '--type=service', '--all'], text=True)
            return result
    except Exception as e:
        return f"Error listing services: {e}" 