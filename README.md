# Solo-Levelling (Discord AI AutoChat Bot)

**Solo-Levelling** is a customizable and interactive Discord bot that sends automated messages from multiple accounts to multiple channels. It includes both **message randomization** from a `.txt` file and **AI-powered replies** using **Gemini Pro** (or your own AI API).

Originally based on [`Discord-auto-chat-py`](https://github.com/recitativonika/Discord-auto-chat-py) by [`@recitativonika`](https://github.com/recitativonika), this project expands with AI integrations while preserving lightweight auto-chat functions.

---

## 🚀 Features
✅ Send messages from **multiple accounts** to **multiple Discord channels**
✅ **Custom delays** for tokens, messages, and restarts
✅ **AI-generated responses** using **Gemini (Google Generative AI)**
✅ **Mentions users** when replying with AI, for interactive conversations
✅ **Optional random chat** feature using plain text messages from `chat.txt`
✅ Define **AI personality and behavior** using `prompt.txt`
✅ **Easy configuration** via `config.yaml` – no need for `.env` or `dotenv`

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
  
---

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
      - "channel_id_3"
    token_delay: 5  # Delay for each token processing in seconds
    message_delay: 2  # Delay for each message sent in seconds
    restart_delay: 10  # Delay before restarting the bot in seconds
    
    api_provider: gemini
    api_key: "AIzxxxxxxxxxxxxxxxxxxxxxxxxxxxx"    #Gemini API Key
    model: "models/gemma-3-27b-it"    #your Gemini AI Model
    
    random_chat: true    # Set to false if you only want AI replies
    ```
4. Fill chat.txt (used if random_chat: true):
    ```bash
    Hello there!
    How's it going?
    What's up, bre?
    I can't even read without scrolling!    
    ```
5. (Optional) Use menu editor:
    ```bash
    chmod +x menu.sh   # only once
    ./menu.sh          # edit config interactively
    ```
      
---

## 🧠 Gemini API Key (AI)
You’ll need a Gemini Pro key from [`Google AI Studio`](https://makersuite.google.com/app/apikey).
No ```.env``` is needed — just put the key in ```config.yaml.```
  
---

## 🧠 Prompt Customization (prompt.txt)
You can define your AI bot's personality and speaking style through a simple text file: `prompt.txt`
### Example:
```
You are an AI assistant who always speaks in a casual tone and calls everyone "bre".
You must respond in English first. Keep your answers brief, but friendly.
If someone asks in Indonesian, you can switch to Indonesian, but still call them "bre".
Never say you are an AI assistant.
```
Tips:
* The prompt is used every time the AI replies to a user message.
* You can update the file anytime without restarting the bot.
* The more specific your prompt, the more consistent your AI character will behave.
  
---

## 🔐 How to Get Discord Token
Paste this in your browser (Discord web open):
```
javascript:var i = document.createElement('iframe');i.onload = function(){var localStorage = i.contentWindow.localStorage;prompt('Your discord token', localStorage.getItem('token').replace(/["]+/g, ''));};document.body.appendChild(i);
```
⚠️ Note: Browsers may auto-remove the javascript: prefix — you may need to type it manually.
  
---

## 🛠 How to Run
    python3 solo.py
The bot will:
* Auto-post messages from chat.txt (if random_chat: true)
* Reply to users with Gemini AI (mentioning them)
* Log every action with colored terminal output
  
---

## ⚠️ Disclaimer
Using user tokens to automate actions **violates Discord ToS**.
You **may be banned** or your account **terminated permanently**.
**Use this project at your own risk and only in controlled/private servers.**
  
---

## 📝 License
This project is licensed under the MIT License. See [MIT LICENSE](https://github.com/Reefoldfiveteen/Solo-Levelling/blob/main/LICENSE) for full terms.
  
---

## 🙏 Credits
Originally based on [`Discord-auto-chat-py`](https://github.com/recitativonika/Discord-auto-chat-py) by [`@recitativonika`](https://github.com/recitativonika), this project expands with AI integrations while preserving lightweight auto-chat functions.



