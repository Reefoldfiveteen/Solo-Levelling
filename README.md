# Solo-Levelling (Discord AI AutoChat Bot)

**Solo-Levelling** is a customizable and interactive Discord bot that sends automated messages from multiple accounts to multiple channels. It includes both **message randomization** from a `.txt` file and **AI-powered replies** using **Gemini Pro** (or your own AI API).

Originally based on [`Discord-auto-chat-py`](https://github.com/recitativonika/Discord-auto-chat-py) by @recitativonika, this project expands with AI integrations while preserving lightweight auto-chat functions.

---

## 🚀 Features

- ✅ Send messages from multiple accounts to multiple channels
- ✅ Custom delays for tokens, messages, and restarts
- ✅ AI-generated responses via Gemini (Google AI)
- ✅ Mentions users when replying with AI
- ✅ Optional: random chat feature from `chat.txt`

---

## 🔧 Prerequisites

- Python 3.6 or higher
- Required libraries:
- requests>=2.31.0
  ```bash
  PyYAML>=6.0
  colorama>=0.4.6
  google-generativeai>=0.5.0
  discord.py>=2.3.2
  ```

