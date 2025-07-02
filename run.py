#!/usr/bin/env python3
"""
Discord Auto‑Chat Bot (simple)
==============================
Versi ringan tanpa opsi menu & tanpa flag "shuffle".
Hanya membaca **config.ini** standar:

[discord]
# bot token (wajib)
token = YOUR_TOKEN
# target channel ID (wajib)
channel_id = 123456789012345678  ; bisa tambahkan komentar setelah ;

[bot]
interval_seconds = 60            ; jeda antar pesan
messages_file   = messages.txt   ; file berisi 1 baris = 1 pesan

— Fitur —
• Pilih pesan secara acak dari `messages_file`.
• Abaikan komentar setelah `;` atau `#` pada nilai numerik.
• Log output ke stdout.

Jalankan:
    python3 run.py
"""
from __future__ import annotations

import asyncio
import configparser
import logging
import random
import re
from pathlib import Path
from typing import List

import discord

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

CONFIG_PATH = Path(__file__).with_name("config.ini")
COMMENT_RE = re.compile(r"[;#].*$")  # hapus komentar ujung baris


def clean(value: str | None) -> str:
    """Hilangkan komentar & spasi."""
    if value is None:
        return ""
    return COMMENT_RE.sub("", value).strip()


def load_config() -> tuple[str, int, int, Path]:
    cfg = configparser.ConfigParser()
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"config.ini tidak ditemukan di {CONFIG_PATH}")
    cfg.read(CONFIG_PATH)

    token = clean(cfg["discord"].get("token"))
    if not token:
        raise ValueError("token di [discord] wajib diisi")

    try:
        channel_id = int(clean(cfg["discord"].get("channel_id")))
    except (TypeError, ValueError):
        raise ValueError("channel_id harus berupa integer")

    interval = int(clean(cfg["bot"].get("interval_seconds", "60")))
    messages_file = Path(clean(cfg["bot"].get("messages_file", "messages.txt")))
    return token, channel_id, interval, messages_file


def load_messages(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"File pesan tidak ditemukan: {path}")
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        raise ValueError("messages_file kosong – isi setidaknya 1 baris pesan")
    return lines


async def main() -> None:
    token, channel_id, interval, messages_path = load_config()
    messages = load_messages(messages_path)

    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        channel = client.get_channel(channel_id)
        if channel is None:
            logging.error("Channel %s tidak ditemukan", channel_id)
            await client.close()
            return
        logging.info("Bot online sebagai %s, posting ke #%s setiap %ss", client.user, channel_id, interval)
        while not client.is_closed():
            msg = random.choice(messages)
            try:
                await channel.send(msg)
                logging.info("Kirim: %s", msg)
            except discord.HTTPException as e:
                logging.error("Gagal kirim: %s", e)
            await asyncio.sleep(interval)

    client.run(token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDihentikan pengguna")
