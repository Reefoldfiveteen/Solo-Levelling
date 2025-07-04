#!/usr/bin/env python3
"""
AI‑Powered Discord Auto‑Reply Bot (config‑only)
==============================================
• Baca **semua** pengaturan, termasuk `openai_api_key`, dari *config.yaml* – tidak
  perlu file `.env`.
• Tetap support multi‑token, multi‑channel, delay, restart.
• Perlu `Message Content Intent` aktif di portal Discord.

----- config.yaml contoh -----
```yaml
token:
  - "BOT_TOKEN_1"
  - "BOT_TOKEN_2"
channel_id:
  - "1300291026673729548"
  - "1300291026673729549"
openai_api_key: "sk‑XXXXXXXXXXXXXXXXXXXX"
# optional (detik)
message_delay: 2
restart_delay: 10
```
--------------------------------
Dependensi:
    pip install -U discord.py openai pyyaml
"""
from __future__ import annotations

import asyncio
import logging
import random
from pathlib import Path
from typing import List

import discord
import openai
import yaml

CFG_FILE = Path(__file__).with_name("config.yaml")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# -------------------- Helpers --------------------------

def load_cfg() -> dict:
    if not CFG_FILE.exists():
        raise FileNotFoundError("config.yaml not found")
    with CFG_FILE.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

async def ask_gpt(prompt: str) -> str:
    resp = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120,
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()

# -------------------- Worker ---------------------------
async def run_bot(token: str, channel_ids: List[int], message_delay: int, restart_delay: int):
    intents = discord.Intents.default(); intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logging.info("[%s] Connected", token[:8])

    @client.event
    async def on_message(msg: discord.Message):
        if msg.author == client.user or msg.channel.id not in channel_ids:
            return
        prompt = f"Reply conversationally (max 1‑2 sentences). Message: '{msg.content}'"
        try:
            reply = await ask_gpt(prompt)
            await asyncio.sleep(random.uniform(0, message_delay))
            await msg.reply(reply, mention_author=False)
            logging.info("[%s] Replied in #%s", token[:8], msg.channel.id)
        except Exception as exc:
            logging.error("GPT/Discord error: %s", exc)

    while True:
        try:
            await client.start(token)
        except Exception as err:
            logging.error("[%s] Disconnect: %s → restart in %ss", token[:8], err, restart_delay)
            await asyncio.sleep(restart_delay)
        else:
            break

# -------------------- Main -----------------------------
async def main():
    cfg = load_cfg()
    tokens = cfg.get("token") or []
    chan_ids = [int(c) for c in cfg.get("channel_id", [])]
    api_key = cfg.get("openai_api_key")
    if not (tokens and chan_ids and api_key):
        raise ValueError("token, channel_id, and openai_api_key must be set in config.yaml")
    openai.api_key = api_key
    msg_delay = int(cfg.get("message_delay", 2))
    rest_delay = int(cfg.get("restart_delay", 10))

    tasks = [run_bot(t, chan_ids, msg_delay, rest_delay) for t in tokens]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped by user")
