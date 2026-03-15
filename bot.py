import os
import telebot
import time
import random
import yt_dlp

def download_from_url(url):
    # This adds a random 3-7 second delay before starting
    time.sleep(random.randint(3, 7))
    
    ydl_opts = {
        # Grabs best quality up to 720p
        'format': 'best[height<=720]/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        
        # Updated bypass for 2026 (using iOS and Mobile Web clients)
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'mweb'],
            }
        },
        'headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1'
        }
    }

    # IMPORTANT: These lines must be indented to stay inside the function
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# 1. Initialize the bot
TOKEN = os.getenv('BOT_TOKEN') 
bot = telebot.TeleBot(TOKEN)

# 2. Handle messages
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    url = message.text
    
    if "youtube.com" in url or "youtu.be" in url:
        bot.reply_to(message, "⏳ Processing your video... please wait.")
        try:
            file_path = download_from_url(url)
            
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video)
            
            # Clean up server space
            if os.path.exists(file_path):
                os.remove(file_path)
            
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")
    else:
        bot.reply_to(message, "Please send a valid YouTube link!")

# 3. Start the bot
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()