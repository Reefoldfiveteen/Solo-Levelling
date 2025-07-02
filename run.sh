#!/usr/bin/env bash
# Interactive helper to create / edit config.ini for Discord Auto‑Chat Bot
# Usage: ./run.sh  -> follow menu
# Run the bot afterwards: python3 run.py

CONFIG_FILE="$(dirname "$0")/config.ini"

# Default values if no config exists yet
TOKEN=""
CHANNEL_ID=""
USER_ID=""
INTERVAL="60"
SHUFFLE="true"
MESSAGES_FILE="messages.txt"

load_config() {
    [[ -f "$CONFIG_FILE" ]] || return 0
    TOKEN=$(grep -E '^token[[:space:]]*=' "$CONFIG_FILE" | head -n1 | cut -d '=' -f2- | xargs)
    CHANNEL_ID=$(grep -E '^channel_id[[:space:]]*=' "$CONFIG_FILE" | head -n1 | cut -d '=' -f2- | xargs)
    USER_ID=$(grep -E '^user_id[[:space:]]*=' "$CONFIG_FILE" | head -n1 | cut -d '=' -f2- | xargs)
    INTERVAL=$(grep -E '^interval_seconds[[:space:]]*=' "$CONFIG_FILE" | head -n1 | cut -d '=' -f2- | xargs)
    SHUFFLE=$(grep -E '^shuffle[[:space:]]*=' "$CONFIG_FILE" | head -n1 | cut -d '=' -f2- | xargs)
    MESSAGES_FILE=$(grep -E '^messages_file[[:space:]]*=' "$CONFIG_FILE" | head -n1 | cut -d '=' -f2- | xargs)
}

save_config() {
cat > "$CONFIG_FILE" <<EOF
[discord]
token = $TOKEN
channel_id = $CHANNEL_ID
user_id = $USER_ID

[bot]
interval_seconds = $INTERVAL
shuffle = $SHUFFLE
messages_file = $MESSAGES_FILE
EOF
    echo "Saved to $CONFIG_FILE"
}

prompt() {
    local varname="$1"; shift
    local prompt_txt="$1"; shift
    local current_value="${!varname}"
    read -rp "$prompt_txt [current: $current_value] > " input
    [[ -z "$input" ]] || printf -v "$varname" '%s' "$input"
}

menu() {
    clear
    echo "==== Discord Auto‑Chat Bot Config ===="
    echo "1) Set bot token"
    echo "2) Set channel ID"
    echo "3) Set user ID"
    echo "4) Set interval seconds"
    echo "5) Toggle shuffle (random messages)"
    echo "6) Set messages file path"
    echo "7) View current config"
    echo "8) Save & exit"
    echo "9) Exit without saving"
    echo "--------------------------------------"
}

load_config

while true; do
    menu
    read -rp "Select option: " choice
    case $choice in
        1) prompt TOKEN "Enter Discord bot token" ;;
        2) prompt CHANNEL_ID "Enter target channel ID" ;;
        3) prompt USER_ID "Enter your Discord user ID" ;;
        4) prompt INTERVAL "Enter seconds between messages" ;;
        5) SHUFFLE=$( [[ "$SHUFFLE" == "true" ]] && echo false || echo true ) ;;
        6) prompt MESSAGES_FILE "Enter messages file path" ;;
        7) echo "--- Current settings ---"; echo "TOKEN=$TOKEN"; echo "CHANNEL_ID=$CHANNEL_ID"; echo "USER_ID=$USER_ID"; echo "INTERVAL=$INTERVAL"; echo "SHUFFLE=$SHUFFLE"; echo "MESSAGES_FILE=$MESSAGES_FILE"; read -rp "Press Enter to continue…" dummy ;;
        8) save_config; exit 0 ;;
        9) echo "No changes saved."; exit 0 ;;
        *) echo "Invalid choice" ; sleep 1 ;;
    esac
done
