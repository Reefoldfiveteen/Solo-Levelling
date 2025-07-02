#!/usr/bin/env python3
"""
Discord Auto‑Chat Bot (enhanced)
================================
Now supports **config.ini** editing via `run.sh` and sequential or random
message sending.

Configuration (`config.ini`)
---------------------------
[discord]
# Your bot token (keep secret!)
token = YOUR_TOKEN_HERE
# Target channel to post
channel_id = 0
# (Optional) user_id if you need it later
user_id = 0

[bot]
# Seconds between messages
interval_seconds = 60
# true  -> pick random message
# false -> cycle in order\shuffle = true
# Text file with one message per line
messages_file = messages.txt

Install deps on Ubuntu 22+:
    pip install -U discord.py

Run:
    python3 run.py
"""

import asyncio
import logging
import random
import configparser
from pathlib import Path
from itertools import cycle

import discord

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
)

CONFIG_PATH = Path(__file__).with_name("config.ini")


def load_config() -> configparser.ConfigParser:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Configuration file {CONFIG_PATH} not found. Create it via run.sh or manually."
        )
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH)
    return cfg


def load_messages(file_path: Path) -> list[str]:
    if not file_path.exists():
        raise FileNotFoundError(f"Message file not found: {file_path}")
    return [
        line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


async def chat_task(
    client: discord.Client,
    channel_id: int,
    messages: list[str],
    interval: int,
    shuffle: bool,
):
    await client.wait_until_ready()
    channel = client.get_channel(channel_id)
    if channel is None:
        logging.error("Channel ID %s not found", channel_id)
        return

    if shuffle:
        msg_iter = None  # we will just call random.choice every time
    else:
        msg_iter = cycle(messages)

    logging.info("Auto‑chat started in <#%s> (shuffle=%s, interval=%ss)", channel_id, shuffle, interval)

    while not client.is_closed():
        content = random.choice(messages) if shuffle else next(msg_iter)
        try:
            await channel.send(content)
            logging.info("Sent: %s", content)
        except discord.HTTPException as e:
            logging.error("Failed to send message: %s", e)
        await asyncio.sleep(interval)


def main():
    cfg = load_config()

    token = cfg["discord"]["token"]
    channel_id = int(cfg["discord"]["channel_id"])

    interval = int(cfg["bot"].get("interval_seconds", 60))
    shuffle = cfg["bot"].getboolean("shuffle", fallback=True)
    messages_file = Path(cfg["bot"].get("messages_file", "messages.txt"))

    messages = load_messages(messages_file)

    client = discord.Client(intents=discord.Intents.default())
    client.loop.create_task(chat_task(client, channel_id, messages, interval, shuffle))
    client.run(token)


if __name__ == "__main__":
    main()
