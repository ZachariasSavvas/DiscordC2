import sys
import subprocess

def list_tasks():
    """Return a formatted list of scheduled tasks."""
    try:
        if sys.platform.startswith('win'):
            result = subprocess.check_output(['schtasks'], text=True)
            return result
        else:
            result = subprocess.check_output(['crontab', '-l'], text=True)
            return result
    except Exception as e:
        return f"Error listing tasks: {e}" 