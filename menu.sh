#!/usr/bin/env bash
# Interactive menu to edit config.yaml (multi‑token Discord bot)
# Usage:  ./config_menu.sh        # follow prompts
# Requires: standard POSIX tools (sed, awk) – no external deps.
#
# Supported fields in config.yaml:
#   token:          [list]
#   channel_id:     [list]
#   token_delay:    int
#   message_delay:  int
#   restart_delay:  int
#   messages_file:  string (optional)
#
CFG="$(dirname "$0")/config.yaml"

# Ensure config.yaml exists
if [[ ! -f "$CFG" ]]; then
  cat > "$CFG" <<EOF
token:
  - "YOUR_TOKEN_1"
channel_id:
  - "CHANNEL_ID_1"
token_delay: 5
message_delay: 2
restart_delay: 10
messages_file: messages.txt
EOF
  echo "Created default $CFG"
fi

# Helpers ---------------------------------------------------------------
read_yaml_list() { # $1=key
  awk -v key="$1" 'BEGIN{p=0} $0 ~ "^"key":" {p=1; next} /^[^ ]/ {p=0} p && /-/ {sub(/- /,""); print}' "$CFG"
}

update_scalar() { # $1=key $2=newval
  if grep -q "^$1:" "$CFG"; then
    # replace line
    sed -i "s|^$1:.*|$1: $2|" "$CFG"
  else
    # append
    echo "$1: $2" >> "$CFG"
  fi
}

add_to_list() { # $1=key $2=value
  # if value already exists, skip
  if read_yaml_list "$1" | grep -qx "$2"; then
    echo "Value already exists."; return
  fi
  awk -v key="$1" -v val="$2" '
    BEGIN{added=0}
    {
      print $0;
      if(!added && $0 ~ "^"key":") {getline; print "  - "val; added=1; print $0; next}
    }' "$CFG" > "$CFG.tmp" && mv "$CFG.tmp" "$CFG"
}

remove_from_list() { # $1=key $2=value
  awk -v key="$1" -v val="$2" '
    BEGIN{p=0}
    {
      if($0 ~ "^"key":") {print; p=1; next}
      if(p && /^[^ ]/) {p=0}
      if(p && $0 ~ /- /) {sub(/- /,""); if($0==val) next; else print "  - "$0; next}
      print
    }' "$CFG" > "$CFG.tmp" && mv "$CFG.tmp" "$CFG"
}

pause() { read -rp "Press Enter to continue..." dummy; }

# Menu ------------------------------------------------------------------
while true; do
  clear
  echo "=== config.yaml editor ==="
  echo "File: $CFG"
  echo "---------------------------"
  echo "Tokens:      $(read_yaml_list token | paste -sd, -)"
  echo "Channels:    $(read_yaml_list channel_id | paste -sd, -)"
  echo "token_delay:    $(grep -E '^token_delay:' "$CFG" | awk '{print $2}')"
  echo "message_delay:  $(grep -E '^message_delay:' "$CFG" | awk '{print $2}')"
  echo "restart_delay:  $(grep -E '^restart_delay:' "$CFG" | awk '{print $2}')"
  echo "messages_file:  $(grep -E '^messages_file:' "$CFG" | awk '{print $2}')"
  echo "---------------------------"
  echo "1) Add token"
  echo "2) Remove token"
  echo "3) Add channel ID"
  echo "4) Remove channel ID"
  echo "5) Set token_delay"
  echo "6) Set message_delay"
  echo "7) Set restart_delay"
  echo "8) Set messages_file"
  echo "9) Quit"
  read -rp "Choose option: " opt
  case $opt in
    1) read -rp "Enter new token: " val; [[ -n "$val" ]] && add_to_list token "$val" ; pause;;
    2) read -rp "Token to remove: " val; [[ -n "$val" ]] && remove_from_list token "$val" ; pause;;
    3) read -rp "Enter new channel ID: " val; [[ -n "$val" ]] && add_to_list channel_id "$val" ; pause;;
    4) read -rp "Channel ID to remove: " val; [[ -n "$val" ]] && remove_from_list channel_id "$val" ; pause;;
    5) read -rp "New token_delay (sec): " val; update_scalar token_delay "$val" ; pause;;
    6) read -rp "New message_delay (sec): " val; update_scalar message_delay "$val" ; pause;;
    7) read -rp "New restart_delay (sec): " val; update_scalar restart_delay "$val" ; pause;;
    8) read -rp "Path to messages_file: " val; update_scalar messages_file "$val" ; pause;;
    9) echo "Done."; exit 0;;
    *) echo "Invalid choice"; pause;;
  esac
done
