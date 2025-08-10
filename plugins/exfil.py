def exfiltrate(file_path):
    """Exfiltrate a file (handled in main_c2.py for Discord upload)."""
    if os.path.exists(file_path):
        return f"File {file_path} ready for exfiltration."
    return "File not found!"