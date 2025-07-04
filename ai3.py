#!/usr/bin/env python3
"""
ai.py — Discord Auto‑Reply Bot with Gemini Pro (dup‑safe)
========================================================
• Prompt eksternal `prompt.txt`.
• Tidak reply dobel: objek bot dibuat sekali, sehingga `last_seen_id` tersimpan
  di‑memori sepanjang runtime (tidak reset setiap siklus).
• `random_chat` di config.yaml bisa aktif/nonaktif.
"""
from __future__ import annotations

import random, sys, time, requests, yaml
from pathlib import Path
from typing import List, Dict
from colorama import Fore, init
import google.generativeai as genai

init(autoreset=True)

ascii_art = r"""
   _____ _                 _        _____  _                       _ ____        _   
  / ____(_)               | |      |  __ \(_)                     | |  _ \      | |  
 | (___  _ _ __ ___  _ __ | | ___  | |  | |_ ___  ___ ___  _ __ __| | |_) | ___ | |_ 
  \___ \| | '_ ` _ \| '_ \| |/ _ \ | |  | | / __|/ __/ _ \| '__/ _` |  _ < / _ \| __|
  ____) | | | | | | | |_) | |  __/ | |__| | \__ \ (_| (_) | | | (_| | |_) | (_) | |_ 
 |_____/|_|_| |_| |_| .__/|_|\___| |_____/|_|___/\___\___/|_|  \__,_|____/ \___/ \__|
                    | |                                                              
                    |_|                                                              
"""

print(Fore.CYAN + ascii_art)
print(Fore.GREEN + "Simple DiscordBot + AI Reply (Gemini)")

API_BASE = "https://discord.com/api/v9"
PROMPT_FILE = Path("prompt.txt")

# ─── Load system prompt ─────────────────────────────

def load_system_prompt() -> str:
    if PROMPT_FILE.exists():
        txt = PROMPT_FILE.read_text(encoding="utf-8").strip()
        if txt:
            return txt
    return (
        "You are ChatBuddy, a friendly Discord user who always calls others 'bre'. "
        "Reply in concise English unless the user speaks another language. "
        "Never reveal you're an AI."
    )

SYSTEM_INSTRUCT = load_system_prompt()

# ─── Gemini helpers ────────────────────────────────

def setup_gemini(api_key: str, model_name: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

def ask_gemini(model, user_prompt: str, retry: int = 3):
    prompt = f"{SYSTEM_INSTRUCT}\nUser: {user_prompt}\nReply:"
    for attempt in range(retry):
        try:
            return model.generate_content(prompt, safety_settings={}).text.strip()
        except Exception as e:
            wait = 5 * (attempt + 1)
            print(Fore.YELLOW + f"[WARN] Gemini error: {e}. Retry {wait}s")
            time.sleep(wait)
    return ""

# ─── Discord wrapper ───────────────────────────────
class DiscordBot:
    def __init__(self, token: str):
        self.h = {"authorization": token, "content-type": "application/json"}
        me = requests.get(f"{API_BASE}/users/@me", headers=self.h).json()
        self.username = f"{me['username']}#{me['discriminator']}"; self.uid = me["id"]
        self.last_seen_id: Dict[str, str] = {}  # channel_id -> msg_id

    # ------------------------------------------------
    def send_text(self, channel: str, text: str):
        requests.post(f"{API_BASE}/channels/{channel}/messages", headers=self.h, json={"content": text})

    def reply_to(self, msg: dict, content: str):
        payload = {
            "content": content,
            "message_reference": {
                "message_id": msg["id"],
                "channel_id": msg["channel_id"],
                "guild_id": msg.get("guild_id")
            },
            "allowed_mentions": {"replied_user": True}
        }
        requests.post(f"{API_BASE}/channels/{msg['channel_id']}/messages", headers=self.h, json=payload)

    def recent(self, channel: str, limit: int = 5):
        r = requests.get(f"{API_BASE}/channels/{channel}/messages", headers=self.h, params={"limit": limit})
        return r.json() if r.status_code == 200 else []

    def auto_reply(self, channel: str, model, limit: int, delay: int):
        msgs = self.recent(channel, limit)
        last_id = self.last_seen_id.get(channel)
        for msg in reversed(msgs):
            if msg["author"]["id"] == self.uid or msg["id"] == last_id or msg["author"].get("bot"):
                continue
            ans = ask_gemini(model, msg["content"])
            if ans:
                self.reply_to(msg, ans)
                print(Fore.CYAN + f"[{self.username}] ↪︎ {msg['author']['username']}: {ans[:60]}")
                self.last_seen_id[channel] = msg["id"]
                break  # balas satu kali saja
            time.sleep(delay)

# ─── Util loader ───────────────────────────────────

def load_yaml(f="config.yaml") -> dict:
    with open(f, "r", encoding="utf-8") as fp:
        return yaml.safe_load(fp) or {}

def load_lines(f="chat.txt") -> List[str]:
    p = Path(f)
    return [l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []

# ─── Main ───────────────────────────────────────────

def main():
    cfg = load_yaml()
    tokens = cfg.get("token", [])
    channels = cfg.get("channel_id", [])
    model = setup_gemini(cfg["api_key"], cfg.get("model", "models/gemini-2.5-pro"))
    lines = load_lines()

    td = cfg.get("token_delay", 5); md = cfg.get("message_delay", 2)
    rd = cfg.get("restart_delay", 10); rl = cfg.get("reply_limit", 3)
    enable_random = cfg.get("random_chat", False)

    # ─── Create bot objects once to keep state ─────
    bots = [DiscordBot(tok) for tok in tokens]

    while True:
        for bot in bots:
            try:
                for ch in channels:
                    if enable_random and lines:
                        txt = random.choice(lines)
                        bot.send_text(ch, txt)
                        print(Fore.GREEN + f"[{bot.username}] → #{ch}: {txt[:50]}")
                        time.sleep(md)
                    bot.auto_reply(ch, model, rl, md)
                time.sleep(td)
            except Exception as e:
                print(Fore.RED + f"[CRITICAL] {type(e).__name__}: {e}")
        time.sleep(rd)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped")
