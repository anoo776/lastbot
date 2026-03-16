import os
import telebot
import time
import random
import yt_dlp
import sys

# --- EMERGENCY DEBUG LOG ---
print("--- SYSTEM CHECK STARTING ---")
print(f"Python Version: {sys.version}")
print(f"Files in directory: {os.listdir('.')}")
# ---------------------------

def download_from_url(url):
    time.sleep(random.randint(2, 5))
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'quiet': False, # Changed to False so we can see what YouTube is doing
        'no_warnings': False,
        'nocheckcertificate': True,
        'extractor_args': {'youtube': {'player_client': ['ios']}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

TOKEN = os.getenv('BOT_TOKEN') 

# Check if token actually exists before starting
if not TOKEN:
    print("❌ FATAL ERROR: BOT_TOKEN is missing from Railway Variables!")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    url = message.text
    print(f"📩 Received message: {url}") # This will show in logs
    if "youtube.com" in url or "youtu.be" in url:
        bot.reply_to(message, "⏳ Downloading...")
        try:
            file_path = download_from_url(url)
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"❌ Download Error: {str(e)}")
            bot.reply_to(message, f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 BOT IS OFFICIALLY ALIVE AND POLLING...")
    bot.infinity_polling()