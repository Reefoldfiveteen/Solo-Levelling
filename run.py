#!/usr/bin/env python3
"""
Discord Auto‑Chat Bot (robust)
==============================
- Reads **config.ini**
- Sends messages to a Discord channel, in random or sequential order
- Works even if config values have trailing comments (e.g. `channel_id = 123 ; note`)

Run:
    python3 run.py
Dependencies:
    pip install -U discord.py
"""
from __future__ import annotations

import asyncio
import configparser
import logging
import random
import re
from itertools import cycle
from pathlib import Path
from typing import List

import discord

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
)

CONFIG_PATH = Path(__file__).with_name("config.ini")
COMMENT_RE = re.compile(r"[;#].*$")  # strip anything after ; or #


def clean(value: str) -> str:
    """Return *value* without inline comments or surrounding whitespace."""
    return COMMENT_RE.sub("", value).strip()


def load_config() -> configparser.ConfigParser:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Configuration file {CONFIG_PATH} not found. Create it via run.sh or manually."
        )
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH)
    return cfg


def load_messages(file_path: Path) -> List[str]:
    if not file_path.exists():
        raise FileNotFoundError(f"Message file not found: {file_path}")
    return [
        line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


async def chat_task(
    client: discord.Client,
    channel_id: int,
    messages: List[str],
    interval: int,
    shuffle: bool,
):
    await client.wait_until_ready()
    channel = client.get_channel(channel_id)
    if channel is None:
        logging.error("Channel ID %s not found", channel_id)
        return

    iterator = cycle(messages) if not shuffle else None
    logging.info("Chat loop started (channel=%s, shuffle=%s, interval=%ss)", channel_id, shuffle, interval)

    while not client.is_closed():
        content = random.choice(messages) if shuffle else next(iterator)
        try:
            await channel.send(content)
            logging.info("Sent: %s", content)
        except discord.HTTPException as exc:
            logging.error("Send failed: %s", exc)
        await asyncio.sleep(interval)


def main():
    cfg = load_config()

    token = clean(cfg["discord"]["token"])
    try:
        channel_id = int(clean(cfg["discord"]["channel_id"]))
    except ValueError as e:
        raise ValueError(
            "Invalid channel_id in config.ini – must be an integer (comments allowed after ';' or '#')."
        ) from e

    interval = int(clean(cfg["bot"].get("interval_seconds", "60")))
    shuffle = cfg["bot"].getboolean("shuffle", fallback=True)
    messages_file = Path(clean(cfg["bot"].get("messages_file", "messages.txt")))

    messages = load_messages(messages_file)

    client = discord.Client(intents=discord.Intents.default())
    client.loop.create_task(chat_task(client, channel_id, messages, interval, shuffle))
    client.run(token)


if __name__ == "__main__":
    main()
