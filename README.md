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

 ## 📦 Installation
1.  Clone the repo:
    ```bash
    git clone https://github.com/Reefoldfiveteen/Solo-Levelling.git
    cd Solo-Levelling
    ```
2. Install requirements:
    ```bash
    pip install -r requirements.txt
    ```
3. Edit config.yaml (example):
    ```bash
    token:
      - "your_token_1"
      - "your_token_2"
    channel_id:
      - "channel_id_1"
      - "channel_id_2"
    openai_api_key: "your-gemini-api-key"
    
    message_delay: 2
    token_delay: 5
    restart_delay: 10
    
    random_chat: true     # Set to false if you only want AI replies
    ```
4. 

