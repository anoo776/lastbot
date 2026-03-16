import os
import time
import telebot
import requests
from telebot import types

# Configuration
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Cobalt API settings
COBALT_API = "https://api.cobalt.tools/api/json"

def get_video_via_cobalt(url, quality="720"):
    """Requests a direct download link from Cobalt."""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    # Cobalt uses specific strings for quality: "360", "720", "1080", etc.
    payload = {
        "url": url,
        "videoQuality": str(quality),
        "downloadMode": "video",
        "filenameStyle": "pretty"
    }
    
    try:
        response = requests.post(COBALT_API, json=payload, headers=headers)
        data = response.json()
        
        # Cobalt returns 'stream' or 'redirect' if successful
        if data.get('status') in ['stream', 'redirect', 'success']:
            video_url = data.get('url')
            
            # Download the actual file to Railway temporarily
            file_name = f"video_{int(time.time())}.mp4"
            r = requests.get(video_url, stream=True)
            with open(file_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return file_name
        else:
            print(f"Cobalt error: {data.get('text')}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Cobalt Bot Active! 🚀 Send me any link (YouTube, TikTok, Instagram).")

@bot.message_handler(func=lambda m: "http" in m.text)
def handle_link(message):
    url = message.text.strip()
    
    # Create Quality Buttons
    markup = types.InlineKeyboardMarkup()
    # Cobalt supports these specific qualities
    qualities = ["360", "480", "720", "1080"]
    
    for q in qualities:
        # data format: "cb|[quality]|[url]"
        callback_data = f"cb|{q}|{url}"
        markup.add(types.InlineKeyboardButton(text=f"🎬 {q}p", callback_data=callback_data))
        
    bot.send_message(message.chat.id, "Select Quality:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('cb|'))
def process_cobalt_download(call):
    bot.answer_callback_query(call.id, "Processing...")
    _, quality, url = call.data.split('|', 2)
    
    bot.edit_message_text(f"Downloading {quality}p... please wait ⏳", call.message.chat.id, call.message.message_id)
    
    file_path = get_video_via_cobalt(url, quality)
    
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as video:
                bot.send_video(call.message.chat.id, video)
            os.remove(file_path) # Cleanup
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Failed to send video: {e}")
    else:
        bot.edit_message_text("❌ Cobalt couldn't process this link. It might be private or blocked.", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    print("--- COBALT BOT STARTED ---")
    bot.infinity_polling()