import sys
try:
    import psutil
except ImportError:
    psutil = None
import subprocess
import os
import random
import ctypes
import ctypes.wintypes

def list_processes():
    """Return a formatted list of running processes (PID, name, user)."""
    if psutil:
        lines = ["PID\tUSER\tNAME"]
        for p in psutil.process_iter(['pid', 'name', 'username']):
            try:
                lines.append(f"{p.info['pid']}\t{p.info.get('username', '?')}\t{p.info.get('name', '?')}")
            except Exception:
                continue
        return '\n'.join(lines)
    else:
        if sys.platform.startswith('win'):
            result = subprocess.check_output(['tasklist'], text=True)
            return result
        else:
            result = subprocess.check_output(['ps', 'aux'], text=True)
            return result

def inject_code(pid, payload_path):
    """Inject a Python payload into a running process by PID (Windows only)."""
    if not sys.platform.startswith('win'):
        return "Process injection is only supported on Windows."
    
    try:
        # For now, we'll use a simpler approach - just verify the process exists
        # and return success, but the actual injection needs to be implemented differently
        if psutil:
            try:
                process = psutil.Process(pid)
                if not process.is_running():
                    return f"Process {pid} is not running."
            except psutil.NoSuchProcess:
                return f"Process {pid} does not exist."
        
        # For now, just return success but note that actual injection needs work
        return f"Process {pid} verified. Note: Full injection requires additional implementation."
        
    except Exception as e:
        return f"Injection failed: {str(e)}"

def inject_random_process(payload_path, exclude_pid=None):
    """Inject payload into a random .exe process (excluding current or specified PID). Returns (pid, exe_name, result) or (None, None, error)."""
    import sys
    import os
    if not sys.platform.startswith('win'):
        return None, None, "Process injection is only supported on Windows."
    if psutil:
        candidates = []
        for p in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if (
                    p.info['pid'] != os.getpid() and
                    (exclude_pid is None or p.info['pid'] != exclude_pid) and
                    p.info['exe'] and p.info['exe'].lower().endswith('.exe') and
                    'system' not in (p.info['name'] or '').lower() and
                    'wininit' not in (p.info['name'] or '').lower() and
                    'csrss' not in (p.info['name'] or '').lower() and
                    'lsass' not in (p.info['name'] or '').lower() and
                    'services' not in (p.info['name'] or '').lower() and
                    'smss' not in (p.info['name'] or '').lower() and
                    'winlogon' not in (p.info['name'] or '').lower()
                ):
                    candidates.append((p.info['pid'], p.info['exe']))
            except Exception:
                continue
    else:
        return None, None, "psutil required for random process selection."
    if not candidates:
        return None, None, "No suitable process found."
    import random
    pid, exe_name = random.choice(candidates)
    result = inject_code(pid, payload_path)
    return pid, exe_name, result 