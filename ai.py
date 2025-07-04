#!/usr/bin/env python3
"""
ai.py ‑ Discord Auto‑Reply Bot with **Gemini Pro**
=================================================
• Kirim pesan acak (optional) dari *chat.txt* ke channel‑channel yang dipilih.  
• Baca pesan terbaru & balas otomatis memakai **Google Gemini Pro** via AI Studio API.  
• Semua pengaturan ada di **config.yaml** – tidak perlu file .env.

Contoh *config.yaml*
--------------------
```yaml
token:               # user token (self‑bot) *atau* bot token
  - "YOUR_DISCORD_TOKEN"
channel_id:
  - "1300291026673729548"
  - "1300291026673729549"

# AI provider
api_provider: gemini      # saat ini hanya "gemini" yang didukung
api_key: "AIzaXXXXXXXXXXXXXXXXXXXXXXXX"   # key dari https://aistudio.google.com/
model: "gemini-pro"       # model name (default gemini-pro)

# Delay settings (detik)
token_delay: 5
message_delay: 2
restart_delay: 10
reply_limit: 3            # max pesan per siklus yang di‑reply per channel
```

Dependensi
----------
```bash
pip install -U requests pyyaml colorama google-generativeai
```
"""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path
from typing import List, Dict, Set

import requests
import yaml
from colorama import Fore, init

try:
    import google.generativeai as genai
except ImportError:
    print("[ERROR] google-generativeai belum ter‑install. Jalankan: pip install google-generativeai")
    sys.exit(1)

init(autoreset=True)

# ---------- Konstanta & ASCII ----------
API_BASE = "https://discord.com/api/v9"
ASCII = r"""
  ____  _           _ _           _           _   _         ____        _  
 |  _ \(_)         | | |         | |         | | | |       |  _ \      | | 
 | |_) |_ _ __   __| | | ___  ___| |__   __ _| |_| |_ _   _| |_) | ___ | |_ 
 |  _ <| | '_ \ / _` | |/ _ \/ __| '_ \ / _` | __| __| | | |  _ < / _ \| __|
 | |_) | | | | | (_| | |  __/\__ \ | | | (_| | |_| |_| |_| | |_) | (_) | |_ 
 |____/|_|_| |_|\__,_|_|\___||___/_| |_|\__,_|\__|\__|\__, |____/ \___/ \__|
                                                       __/ |                
                                                      |___/                 
"""
print(Fore.CYAN + ASCII)
print(Fore.GREEN + "Discord Bot + Gemini Pro Auto‑Reply")
print()

# ---------- Helper: Gemini -----------

def setup_gemini(api_key: str, model_name: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


def ask_gemini(model, prompt: str, max_try: int = 3) -> str:
    for attempt in range(max_try):
        try:
            resp = model.generate_content(prompt, safety_settings={})
            return resp.text.strip()
        except Exception as exc:  # pylint: disable=broad-except
            wait = 5 * (attempt + 1)
            print(Fore.YELLOW + f"[WARN] Gemini error {type(exc).__name__}: retry in {wait}s")
            time.sleep(wait)
    return ""

# ---------- Discord REST wrapper ------
class DiscordBot:
    def __init__(self, token: str):
        self._token = token
        self._h = {"authorization": token, "content-type": "application/json"}
        me = requests.get(f"{API_BASE}/users/@me", headers=self._h).json()
        self.username = f"{me['username']}#{me['discriminator']}"
        self.user_id = me["id"]
        self._seen: Dict[str, Set[str]] = {}

    def send(self, channel_id: str, content: str):
        payload = {"content": content}
        requests.post(f"{API_BASE}/channels/{channel_id}/messages", headers=self._h, json=payload)

    def recent(self, channel_id: str, limit: int = 5):
        r = requests.get(f"{API_BASE}/channels/{channel_id}/messages", headers=self._h, params={"limit": limit})
        return r.json() if r.status_code == 200 else []

    def auto_reply(self, channel: str, model, reply_limit: int, msg_delay: int):
        messages = self.recent(channel, reply_limit)
        seen = self._seen.setdefault(channel, set())
        for msg in reversed(messages):
            if msg["author"]["id"] == self.user_id or msg["id"] in seen:
                continue
            prompt = f"Reply conversationally, max 1‑2 sentences: {msg['content']}"
            reply = ask_gemini(model, prompt)
            if reply:
                self.send(channel, reply)
                print(Fore.CYAN + f"[{self.username}] ↪︎ {msg['author']['username']}: {reply[:60]}")
            seen.add(msg["id"])
            time.sleep(msg_delay)

# ---------- Util load file -----------

def load_yaml(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_lines(path: str = "chat.txt") -> List[str]:
    p = Path(path)
    return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()] if p.exists() else []

# ---------- Main loop ---------------

def main():
    cfg = load_yaml()

    tokens = cfg.get("token") or []
    channels = cfg.get("channel_id") or []
    provider = cfg.get("api_provider", "gemini").lower()
    api_key = cfg.get("api_key", "")
    model_name = cfg.get("model", "gemini-pro")

    if provider != "gemini":
        print(Fore.RED + "[ERROR] Currently only 'gemini' provider is implemented.")
        sys.exit(1)
    if not api_key:
        print(Fore.RED + "[ERROR] api_key missing in config.yaml")
        sys.exit(1)

    gemini_model = setup_gemini(api_key, model_name)
    lines = load_lines()

    token_delay = cfg.get("token_delay", 5)
    msg_delay = cfg.get("message_delay", 2)
    restart_delay = cfg.get("restart_delay", 10)
    reply_limit = cfg.get("reply_limit", 3)

    while True:
        for tok in tokens:
            try:
                bot = DiscordBot(tok)
                # random chat
                for ch in channels:
                    if lines:
                        txt = random.choice(lines)
                        bot.send(ch, txt)
                        print(Fore.GREEN + f"[{bot.username}] → #{ch}: {txt[:60]}")
                        time.sleep(msg_delay)
                # ai reply
                for ch in channels:
                    bot.auto_reply(ch, gemini_model, reply_limit, msg_delay)
                print(Fore.YELLOW + f"[INFO] sleep {token_delay}s next token …")
                time.sleep(token_delay)
            except Exception as exc:
                print(Fore.RED + f"[CRITICAL] token error {type(exc).__name__}: {exc}")
        print(Fore.YELLOW + f"[INFO] restart loop in {restart_delay}s …")
        time.sleep(restart_delay)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped by user")
