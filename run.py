#!/usr/bin/env python3
"""
Discord Auto‑Chat Bot
====================
Runs on Python 3.  Reads settings from **config.ini** in the same folder and
periodically sends a random message from *messages.txt* to the configured
channel.

Usage (after installing dependencies):
    python3 run.py

-----
Configuration file (config.ini)
--------------------------------
[discord]
# **REPLACE with your real bot token – keep it secret!**
token = OTMzMjYyOTIzNzg1MTgzMjUz.GErSUP.qleITLL3KDiZ-hxSNHQYyo-B-W4TdNN49zhZQs
# Channel where the bot will chat
channel_id = 1300291026673729548

[bot]
# Seconds to wait between messages (default 60)
interval_seconds = 60
# Path to file that contains one message per line
messages_file = messages.txt

-----
Dependencies
------------
- python 3.10+ (Ubuntu 22 ships 3.10)
- discord.py ≥ 2.3  (pip install -U discord.py)

Optionally add `python-dotenv` if you prefer to load the token from an env file.

-----
File *messages.txt*
-------------------
Create a plain‑text file next to run.py; each non‑empty line will be chosen at
random and sent to the channel:

    Hello bre!
    Apa kabar semuanya?
    Selamat coding 😎

-----
Systemd service (optional)
-------------------------
To run 24×7, create `/etc/systemd/system/discord‑bot.service` with:

    [Unit]
    Description=Discord Auto‑Chat Bot
    After=network.target

    [Service]
    WorkingDirectory=/opt/discord‑bot
    ExecStart=/usr/bin/python3 /opt/discord‑bot/run.py
    Restart=always
    User=yourusername

    [Install]
    WantedBy=multi-user.target

Then `sudo systemctl enable --now discord‑bot`.
"""

import asyncio
import logging
import random
import configparser
from pathlib import Path

import discord

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
)

CONFIG_PATH = Path(__file__).with_name("config.ini")


def load_config() -> configparser.ConfigParser:
    """Read and return the INI configuration."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_PATH}. Create it from the sample above."
        )

    parser = configparser.ConfigParser()
    parser.read(CONFIG_PATH)
    return parser


def load_messages(file_path: Path) -> list[str]:
    """Load messages (one per line) from *file_path* and return a list."""
    if not file_path.exists():
        raise FileNotFoundError(f"Message file not found: {file_path}")

    return [
        line.strip()
        for line in file_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


async def chat_task(
    client: discord.Client,
    channel_id: int,
    messages: list[str],
    interval: int,
):
    """Background loop: send a random message every *interval* seconds."""
    await client.wait_until_ready()
    channel = client.get_channel(channel_id)
    if channel is None:
        logging.error("Could not find channel with ID %s", channel_id)
        return

    logging.info("Auto‑chat loop started for <#%s>", channel_id)
    while not client.is_closed():
        content = random.choice(messages)
        try:
            await channel.send(content)
            logging.info("Sent: %s", content)
        except discord.HTTPException as exc:
            logging.error("Discord error: %s", exc)
        await asyncio.sleep(interval)


def main() -> None:
    cfg = load_config()

    token = cfg["discord"]["token"]
    channel_id = int(cfg["discord"]["channel_id"])

    interval = int(cfg.get("bot", "interval_seconds", fallback="60"))
    messages_file = Path(cfg.get("bot", "messages_file", fallback="messages.txt"))

    messages = load_messages(messages_file)

    intents = discord.Intents.default()  # no privileged intents needed for sending messages

    client = discord.Client(intents=intents)

    # Launch background task after the client starts
    client.loop.create_task(chat_task(client, channel_id, messages, interval))

    client.run(token)


if __name__ == "__main__":
    main()
