# Discord C2 - Advanced Command & Control Framework

A sophisticated Discord-based Command & Control (C2) framework with advanced anti-reverse engineering capabilities, process injection, and comprehensive system reconnaissance tools.

## Features

### Core C2 Capabilities
- **Discord-based communication** - Secure command execution via Discord channels
- **Encrypted communication** - All commands and responses encrypted with Fernet
- **Multi-platform support** - Windows, Linux, and macOS compatibility
- **Standalone executables** - No Python installation required on target systems

### System Reconnaissance
- **Process management** - List, inject, and manipulate running processes
- **System information** - Detailed CPU, GPU, RAM, and OS information
- **File operations** - Upload, download, and exfiltrate files
- **Screenshot & camera** - Capture screen and webcam snapshots
- **Video recording** - Record screen and camera clips (up to 30 seconds)
- **Keylogging** - Configurable duration keylogger with readable output

### Advanced Persistence & Evasion
- **Multiple persistence methods** - Registry, scheduled tasks, startup folder
- **Process injection** - Inject payload into random processes for stealth
- **Anti-analysis measures** - Timing checks, debugger detection
- **Event log clearing** - Remove traces after operations
- **Advanced obfuscation** - Variable name obfuscation and code protection

### Security Features
- **Maximum anti-reverse engineering** - Encrypted API keys, obfuscated code
- **Build-time encryption** - Custom build keys for additional protection
- **Anti-debugging** - Detection of analysis tools and debuggers
- **UPX compression** - Additional layer of obfuscation
- **Debug symbol stripping** - Remove analysis metadata

## Requirements

### For Building
```bash
pip install -r requirements.txt
```

### Dependencies
- `discord.py==2.3.2` - Discord API wrapper
- `cryptography==42.0.5` - Encryption and security
- `pynput==1.7.6` - Keylogging capabilities
- `pyautogui==0.9.54` - Screenshot and automation
- `numpy==1.26.4` - Numerical operations
- `opencv-python==4.9.0.80` - Camera and video recording
- `requests==2.31.0` - HTTP requests
- `pyinstaller==5.13.0` - Executable generation
- `psutil==5.9.8` - Process management

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Discord-C2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your Discord bot**
   - Create a Discord application at https://discord.com/developers/applications
   - Create a bot and get your bot token
   - Add the bot to your server with appropriate permissions

4. **Set up configuration**
   - Create an `api.json` file with your configuration (see Configuration section)
   - Or run the builder interactively

## Configuration

Create an `api.json` file with the following structure:

```json
{
  "bot_token": "YOUR_BOT_TOKEN",
  "server_id": "YOUR_SERVER_ID",
  "category_name": "Endpoints",
  "authorized_users": "YOUR_DISCORD_USER_ID",
  "encryption_key": "YOUR_ENCRYPTION_KEY",
  "persistence": "none",
  "output_format": "exe",
  "obfuscate": true,
  "build_key": "YOUR_BUILD_ENCRYPTION_KEY"
}
```

### Configuration Options
- **bot_token**: Your Discord bot token
- **server_id**: Target Discord server ID
- **category_name**: Category name for organizing endpoints
- **authorized_users**: Comma-separated list of authorized Discord user IDs
- **encryption_key**: Fernet key for command encryption (leave blank to auto-generate)
- **persistence**: Persistence method (registry/schtask/startup/none)
- **output_format**: Output format (exe/ps1/bat/py)
- **obfuscate**: Enable code obfuscation (true/false)
- **build_key**: Additional encryption key for build-time protection

## Building

### Generate Payload
```bash
python builder.py
```

The builder will:
1. Read configuration from `api.json` or prompt for input
2. Encrypt all sensitive values with the build key
3. Apply advanced obfuscation
4. Generate the payload in your chosen format

### Output Options
- **exe**: Standalone Windows executable (recommended)
- **ps1**: PowerShell script
- **bat**: Batch file
- **py**: Python script

## Available Commands

### System Information
- `!info` - Detailed system information (CPU, GPU, RAM, OS)
- `!env` - Dump environment variables
- `!processes` - List running processes
- `!tasks` - List scheduled tasks
- `!services` - List Windows services

### File Operations
- `!upload <destination>` - Upload file to client (attach file to message)
- `!download <file>` - Download file from client
- `!exfil <file>` - Exfiltrate file with encoding

### System Control
- `!cmd <command>` - Execute shell command
- `!shell <ip:port>` - Spawn reverse shell
- `!sleep <seconds>` - Sleep for specified duration
- `!kill` - Terminate the client

### Surveillance
- `!screenshot` - Take screenshot
- `!camera` - Take webcam snapshot
- `!clip [computer|camera] [seconds]` - Record video (max 30s)
- `!keylog [seconds]` - Start keylogger (default 10s)

### Advanced Operations
- `!inject <pid> <payload>` - Inject payload into process
- `!hide` - Inject into random process and kill self
- `!persist [method]` - Setup persistence (registry/schtask/startup/all)
- `!fullclear` - Remove all persistence methods

### Utility
- `!help` - Show all available commands
- `!delete` - Toggle auto-deletion of responses
- `!update <url>` - Update code from URL

## Security Features

### Anti-Reverse Engineering
- **Encrypted Configuration**: All sensitive values encrypted with build-time keys
- **Advanced Obfuscation**: Variable names and function names randomized
- **Anti-Analysis**: Detection of debugging tools and analysis environments
- **UPX Compression**: Additional layer of obfuscation
- **Debug Symbol Stripping**: Remove analysis metadata

### Evasion Techniques
- **Process Injection**: Hide in legitimate processes
- **Event Log Clearing**: Remove traces after operations
- **Multiple Persistence**: Registry, scheduled tasks, startup folder
- **Timing Checks**: Detect suspicious execution patterns

### Communication Security
- **Encrypted Commands**: All commands encrypted with Fernet
- **Authorized Users**: Restrict access to specific Discord users
- **Auto-deletion**: Optional automatic message deletion

## Project Structure

```
Discord-C2/
├── main_c2.py          # Main C2 client
├── builder.py          # Payload builder
├── api.json           # Configuration file
├── requirements.txt   # Python dependencies
├── README.md         # This file
├── utils/            # Utility modules
│   ├── encryption.py    # Encryption utilities
│   ├── evasion.py       # Evasion techniques
│   ├── persistence.py   # Persistence methods
│   └── ...
└── plugins/          # Feature modules
    ├── processes.py     # Process management
    ├── screenshot.py    # Screenshot/camera
    ├── keylog.py        # Keylogging
    └── ...
```

## Legal Disclaimer

This tool is provided for **educational and authorized testing purposes only**. Users are responsible for ensuring they have proper authorization before using this tool on any system. The authors are not responsible for any misuse of this software.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Important Notes

1. **Authorization Required**: Only use on systems you own or have explicit permission to test
2. **Discord Terms**: Ensure compliance with Discord's Terms of Service
3. **Local Laws**: Respect local laws and regulations regarding cybersecurity tools
4. **Updates**: Keep dependencies updated for security patches
5. **Backup**: Always backup important data before testing

## Troubleshooting

### Common Issues
- **PyInstaller not found**: Install with `pip install pyinstaller`
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Permission errors**: Run as administrator for certain operations
- **Discord connection issues**: Verify bot token and permissions

### Support
For issues and questions, please open an issue on the repository.

---

**Remember**: This tool is for authorized testing and educational purposes only. Always obtain proper permission before use.
