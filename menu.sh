#!/usr/bin/env bash
# menu.sh — interactive editor for config.yaml
# -------------------------------------------
# Manages:
#   • token (list)              • api_provider
#   • channel_id (list)         • api_key
#   • token_delay               • model
#   • message_delay             • random_chat (bool)
#   • restart_delay
CFG="$(dirname "$0")/config.yaml"

create_default() {
cat > "$CFG" <<'EOF'
token:
  - "your_token_1"
  - "your_token_2"

channel_id:
  - "channel_id_1"
  - "channel_id_2"
  - "channel_id_3"

token_delay: 5
message_delay: 2
restart_delay: 10

api_provider: gemini
api_key: "AIzxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
model: "models/gemma-3-27b-it"

random_chat: true
EOF
echo "Created default config.yaml"
}

# create initial file if missing
[[ -f "$CFG" ]] || create_default

# --- simple YAML helpers (indent‑based) -----------
read_list() { awk -v k="$1" 'BEGIN{p=0} $0~"^"k":"{p=1;next} /^[^ ]/{p=0} p&&/-/{sub(/- /,"");print}' "$CFG"; }
update_scalar(){ grep -q "^$1:" "$CFG" && sed -i "s|^$1:.*|$1: $2|" "$CFG" || echo "$1: $2" >>"$CFG"; }
add_list()   { read_list "$1"|grep -qx "$2" && { echo "Already exists";return; }
  awk -v k="$1" -v v="$2" 'BEGIN{a=0}{print;$0~"^"k":"&&!a{getline;print "  - "v;print;a=1}}' "$CFG" >"$CFG.tmp" && mv "$CFG.tmp" "$CFG"; }
rm_list() { awk -v k="$1" -v v="$2" 'BEGIN{p=0}
  $0~"^"k":"{print;p=1;next}
  /^[^ ]/{p=0}
  p&&/-/{sub(/- /,""); if($0==v)next; print "  - "$0; next}
  {print}' "$CFG" >"$CFG.tmp" && mv "$CFG.tmp" "$CFG"; }

pause(){ read -rp "Press Enter to continue…"; }

# --- main menu ------------------------------------
while true; do
  clear
  echo "=== Solo‑Levelling config editor ==="
  echo "Tokens       : $(read_list token | paste -sd, -)"
  echo "Channel IDs  : $(read_list channel_id | paste -sd, -)"
  echo "token_delay  : $(grep -E '^token_delay:'   "$CFG"|awk '{print $2}')"
  echo "message_delay: $(grep -E '^message_delay:' "$CFG"|awk '{print $2}')"
  echo "restart_delay: $(grep -E '^restart_delay:' "$CFG"|awk '{print $2}')"
  echo "api_provider : $(grep -E '^api_provider:'  "$CFG"|awk '{print $2}')"
  echo "api_key      : $(grep -E '^api_key:'       "$CFG"|awk '{print $2}')"
  echo "model        : $(grep -E '^model:'         "$CFG"|awk '{print $2}')"
  echo "random_chat  : $(grep -E '^random_chat:'   "$CFG"|awk '{print $2}')"
  echo "-------------------------------------"
  cat <<'MENU'
1)  Add token              7)  Set message_delay
2)  Remove token           8)  Set restart_delay
3)  Add channel ID         9)  Set api_provider
4)  Remove channel ID      10) Set api_key
5)  Set token_delay        11) Set model
6)  Toggle random_chat     12) Quit
MENU
  read -rp "Choose option: " opt
  case $opt in
    1) read -rp "New token: " v && [[ $v ]] && add_list token "$v"; pause;;
    2) read -rp "Token to remove: " v && [[ $v ]] && rm_list token "$v"; pause;;
    3) read -rp "New channel ID: " v && [[ $v ]] && add_list channel_id "$v"; pause;;
    4) read -rp "Channel ID to remove: " v && [[ $v ]] && rm_list channel_id "$v"; pause;;
    5) read -rp "token_delay (sec): " v && update_scalar token_delay "$v"; pause;;
    6) cur=$(grep -E '^random_chat:' "$CFG"|awk '{print $2}')
       [[ $cur == true ]] && update_scalar random_chat false || update_scalar random_chat true; pause;;
    7) read -rp "message_delay (sec): " v && update_scalar message_delay "$v"; pause;;
    8) read -rp "restart_delay (sec): " v && update_scalar restart_delay "$v"; pause;;
    9) read -rp "api_provider (gemini): " v && update_scalar api_provider "$v"; pause;;
   10) read -rp "api_key: " v && update_scalar api_key "\"$v\""; pause;;
   11) read -rp "model (e.g. models/gemma-3-27b-it): " v && update_scalar model "\"$v\""; pause;;
   12) echo "Done."; exit 0;;
    *) echo "Invalid option"; pause;;
  esac
done
