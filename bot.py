import os
import telebot
import time
import random
import yt_dlp

def download_from_url(url):
    # This adds a random 3-7 second delay before starting
    # It stops YouTube from seeing a "pattern" of bot activity
    time.sleep(random.randint(3, 7))
    ydl_opts = {
        'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
        'outtmpl': 'video_720p.%(ext)s',
        'quiet': True,
        
        # KEY SETTINGS TO PROTECT YOUR IP:
        'extractor_args': {
            'youtube': {
                # We prioritize 'ios' because it is the most stable bypass in 2026
                'player_client': ['ios', 'mweb'],
            }
        },
        # These help bypass basic Cloudflare/Google bot checks
        'nocheckcertificate': True,
        'no_warnings': True,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
    import os
import telebot

# 1. Initialize the bot using the Environment Variable
TOKEN = os.getenv('BOT_TOKEN') 
bot = telebot.TeleBot(TOKEN)

# 2. This tells the bot what to do when it receives a message
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    url = message.text
    
    if "youtube.com" in url or "youtu.be" in url:
        bot.reply_to(message, "⏳ Processing your video... please wait.")
        try:
            # Call your download function
            file_path = download_from_url(url)
            
            # Send the video file back to the user
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video)
            
            # Clean up: delete the file from the server after sending
            os.remove(file_path)
            
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")
    else:
        bot.reply_to(message, "Please send a valid YouTube link!")

# 3. Start the bot and keep it running
print("Bot is running...")
bot.infinity_polling()