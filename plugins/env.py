import os

def dump_env():
    """Return all environment variables as a formatted string."""
    return '\n'.join([f"{k}={v}" for k, v in os.environ.items()]) 