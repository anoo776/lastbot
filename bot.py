import os
import telebot
import time
import random
import yt_dlp

def download_from_url(url):
    time.sleep(random.randint(2, 5))
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'extractor_args': {'youtube': {'player_client': ['android']}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

TOKEN = os.getenv('BOT_TOKEN') 
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    url = message.text
    if "youtube.com" in url or "youtu.be" in url:
        bot.reply_to(message, "⏳ Downloading...")
        try:
            file_path = download_from_url(url)
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")

if __name__ == "main":
    print("Bot is starting...")
    bot.infinity_polling()