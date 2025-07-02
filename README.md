# Solo-Levelling
Discord Solo Levelling
Cara pakai singkat

Siapkan lingkungan

bash
Copy
Edit
sudo apt update
sudo apt install python3 python3-pip -y        # Ubuntu 22 sudah bawa Python 3.10
pip3 install --user discord.py==2.3.2          # pustaka utama
(Kalau mau, bisa bikin virtual‑env lebih rapi.)

Buat config.ini di folder yang sama dengan run.py

ini
Copy
Edit
[discord]
token = xxx
channel_id = xxx   ; channel target

[bot]
interval_seconds = 60              ; jeda antar‑chat (detik)
messages_file = messages.txt       ; daftar kalimat
Siapkan messages.txt
Satu baris = satu chat, contoh:

nginx
Copy
Edit
Halo bre!
Udah ngopi belum?
Coding dulu yuk 😄
Jalankan

bash
Copy
Edit
python3 run.py
Bot akan login, lalu mengirim pesan acak setiap interval_seconds.

Ingin 24×7?
Deploy di screen, tmux, atau systemd service (contoh service unit sudah ada di header file).


chmod +x run.sh   # sekali saja
./run.sh          # buka menu, atur token, channel, jeda, dll
python3 run.py    # jalankan bot
