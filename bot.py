import os
import time
import telebot
import yt_dlp

# 1. Configuration - Get your Bot Token from Railway Environment Variables
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def download_video(url):
    """Downloads a video using cookies from Railway Variables."""
    cookie_path = "cookies.txt"
    cookies_content = os.getenv("COOKIES")
    
    if cookies_content:
        with open(cookie_path, "w") as f:
            f.write(cookies_content)

    ydl_opts = {
        # This says: "Try best MP4 video + M4A audio, otherwise just get the best single file"
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'cookiefile': 'cookies.txt',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'nocheckcertificate': True,
        'quiet': False, # Leave this False so you can see details in Railway logs
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'mweb'],
                'po_token': ['web+password'],
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Bot is awake! Send me a YouTube link to start.")

@bot.message_handler(func=lambda m: "youtube.com" in m.text or "youtu.be" in m.text)
def handle_video(message):
    bot.reply_to(message, "Processing your video... please wait.")
    try:
        file_path = download_video(message.text)
        with open(file_path, 'rb') as video:
            bot.send_video(message.chat.id, video)
        os.remove(file_path)  # Cleanup
    except Exception as e:
        bot.reply_to(message, f"Oops, something went wrong: {str(e)}")

# This is the "Wake Up" block you were looking for!
if __name__ == "__main__":
    print("--- BOT STARTED SUCCESSFULLY ---")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Polling crashed: {e}")
        time.sleep(5)