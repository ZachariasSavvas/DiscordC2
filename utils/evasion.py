import asyncio
import random

async def mimic_behavior(channel):
    """Mimic legitimate bot behavior by posting status updates."""
    messages = [
        "System health check completed.",
        "Monitoring endpoint status...",
        "All systems nominal."
    ]
    while True:
        await channel.send(random.choice(messages))
        await asyncio.sleep(random.randint(300, 600))  # Random delay between 5-10 minutes