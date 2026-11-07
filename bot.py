import requests
import subprocess
import time
import os
import json

# ===== DATA KAMU SUDAH OTOMATIS MASUK =====
TOKEN = "9009087774:AAHt1cbckoroinc8stoASYSLJvcvGyCdz8s"
CHAT_ID = "8784695023"
# ==========================================

URL = f"https://api.telegram.org/bot{TOKEN}/"
torch_state = False # Menyimpan status senter

# Fungsi untuk membuat menu tombol di bawah keyboard
def get_menu():
    keyboard = {
        "keyboard": [
            [{"text": "🔋 Cek Baterai"}, {"text": "⚙️ Info Sistem"}],
            [{"text": "📸 Ambil Foto"}, {"text": "🤳 Selfie Depan"}],
            [{"text": "📍 Lokasi"}, {"text": "📋 Clipboard"}],
            [{"text": "🔦 Senter"}, {"text": "📳 Getarkan HP"}],
            [{"text": "💬 Bantuan"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    return json.dumps(keyboard)

def send_message(text, reply_markup=None, parse_mode="Markdown"):
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(URL + "sendMessage", data=payload)

def send_typing():
    requests.post(URL + "sendChatAction", data={"chat_id": CHAT_ID, "action": "typing"})

def send_photo(filepath, caption=""):
    with open(filepath, 'rb') as f:
        requests.post(URL + "sendPhoto", data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "Markdown"}, files={"photo": f})
    if os.path.exists(filepath): os.remove(filepath)

def send_document(filepath):
    if not os.path.exists(filepath):
        send_message(f"❌ File tidak ditemukan: `{filepath}`")
        return
    with open(filepath, 'rb') as f:
        requests.post(URL + "sendDocument", data={"chat_id": CHAT_ID}, files={"document": f})

def process_command(cmd):
    global torch_state
    cmd = cmd.strip()
    send_typing()
    
    if cmd in ['/start', '/help', '💬 Bantuan']:
        text = (
            "🤖 *Ultimate Remote Bot!*\n\n"
            "Klik tombol di bawah untuk fitur cepat.\n"
            "Atau gunakan perintah rahasia:\n"
            "• `/sh [perintah]` - Jalankan terminal\n"
            "• `/download [path]` - Ambil file dari HP\n"
            "• `/say [teks]` - Suruh HP bicara\n"
            "• `/notify [teks]` - Kirim notif"
        )
        send_message(text, reply_markup=get_menu())
        
    elif cmd in ['/battery', '🔋 Cek Baterai']:
        res = subprocess.run(['termux-battery-status'], capture_output=True, text=True)
        data = json.loads(res.stdout)
        percent, temp, status = data.get('percentage', 0), data.get('temperature', 0), data.get('status', 'Unknown')
        filled = int(percent / 100 * 10)
        bar = "█" * filled + "░" * (10 - filled)
        send_message(f"🔋 *Baterai*\n\n`[{bar}]` *{percent}%*\n🌡️ Suhu: `{temp}°C`\n⚡ Status: `{status}`")

    elif cmd in ['/sysinfo', '⚙️ Info Sistem']:
        ram = subprocess.run(['free', '-h'], capture_output=True, text=True).stdout.split('\n')[1]
        disk = subprocess.run(['df', '-h', '/data'], capture_output=True, text=True).stdout.split('\n')[1]
        send_message(f"⚙️ *Sistem*\n\n🧠 *RAM:*\n`{ram}`\n\n💾 *Storage:*\n`{disk}`")
        
    elif cmd in ['/photo', '📸 Ambil Foto']:
        send_message("📸 _Mengambil foto belakang..._")
        path = os.path.expanduser("~/foto_belakang.jpg")
        subprocess.run(['termux-camera-photo', '-c', '0', path])
        send_photo(path, "📷 *Kamera Belakang*")

    elif cmd in ['/selfie', '🤳 Selfie Depan']:
        send_message("🤳 _Mengambil selfie..._")
        path = os.path.expanduser("~/foto_depan.jpg")
        subprocess.run(['termux-camera-photo', '-c', '1', path])
        send_photo(path, "📷 *Kamera Depan*")

    elif cmd in ['/location', '📍 Lokasi']:
        send_message("📍 _Mencari koordinat GPS..._")
        res = subprocess.run(['termux-location'], capture_output=True, text=True)
        try:
            data = json.loads(res.stdout)
            lat, lon = data.get('latitude'), data.get('longitude')
            send_message(f"📍 *Lokasi HP:*\n[Klik untuk buka Google Maps](https://maps.google.com/?q={lat},{lon})\n\n`Lat: {lat}`\n`Lon: {lon}`")
        except:
            send_message("❌ Gagal dapat lokasi. Pastikan GPS nyala & izin Termux:API aktif.")

    elif cmd in ['/torch', '🔦 Senter']:
        torch_state = not torch_state
        subprocess.run(['termux-torch', 'on' if torch_state else 'off'])
        status = "MENYALA 🔆" if torch_state else "MATI 🌑"
        send_message(f"Senter: *{status}*")

    elif cmd in ['/vibrate', '📳 Getarkan HP']:
        subprocess.run(['termux-vibrate', '-d', '2000'])
        send_message("📳 _HP bergetar selama 2 detik!_")

    elif cmd in ['/clipboard', '📋 Clipboard']:
        res = subprocess.run(['termux-clipboard-get'], capture_output=True, text=True)
        text = res.stdout if res.stdout else "(Kosong)"
        send_message(f"📋 *Isi Clipboard:*\n\n`{text}`")

    # --- Perintah Teks Rahasia ---
    elif cmd.startswith('/sh '):
        shell_cmd = cmd.replace('/sh ', '')
        res = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True)
        output = res.stdout + res.stderr
        if not output: output = "(Tidak ada output)"
        send_message(f"💻 *Output:*\n```\n{output[:4000]}\n```") # Limit 4000 char Telegram

    elif cmd.startswith('/download '):
        path = cmd.replace('/download ', '')
        send_document(path)

    elif cmd.startswith('/say '):
        subprocess.run(['termux-tts-speak', cmd.replace('/say ', '')])
        send_message("🗣️ HP berbicara.")

    elif cmd.startswith('/notify '):
        subprocess.run(['termux-notification', '--title', 'Pesan Telegram', '--content', cmd.replace('/notify ', '')])
        send_message("🔔 Notifikasi terkirim.")

def main():
    print("[*] Ultimate Bot berjalan... Tekan Ctrl+C untuk berhenti.")
    send_message("🚀 *Ultimate Remote HP Aktif!*\nSilakan klik tombol menu di bawah:", reply_markup=get_menu())
    last_update_id = 0
    
    while True:
        try:
            res = requests.get(URL + f"getUpdates?offset={last_update_id}&timeout=30")
            data = res.json()
            if data.get("result"):
                for update in data["result"]:
                    last_update_id = update["update_id"] + 1
                    if "message" in update and "text" in update["message"]:
                        chat_id = str(update["message"]["chat"]["id"])
                        if chat_id == CHAT_ID:
                            process_command(update["message"]["text"])
        except KeyboardInterrupt:
            print("\n[*] Bot dihentikan.")
            break
        except Exception as e:
            time.sleep(3)

if __name__ == "__main__":
    main()
