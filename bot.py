import os
import time
import telebot
import yt_dlp
from telebot import types

# 1. Configuration - Get your Bot Token from Railway Environment Variables
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def get_available_qualities(url):
    """Fetches available resolutions without downloading."""
    ydl_opts = {
        'cookiefile': 'cookies.txt',
        'nocheckcertificate': True,
        'quiet': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [])
        
        # Filter for mp4 formats with video and audio
        available = []
        seen_heights = set()
        for f in formats:
            height = f.get('height')
            # We look for standard qualities and avoid duplicates
            if height and height >= 144 and height not in seen_heights:
                available.append({'height': height, 'format_id': f['format_id']})
                seen_heights.add(height)
        
        # Sort by height (highest quality first)
        return sorted(available, key=lambda x: x['height'], reverse=True), info.get('id')

def download_video(url, format_id):
    """Downloads the specific format chosen by the user."""
    cookie_path = "cookies.txt"
    cookies_content = os.getenv("COOKIES")
    
    if cookies_content:
        with open(cookie_path, "w") as f:
            f.write(cookies_content)

    ydl_opts = {
        # Uses the specific format_id from the button click
        'format': f'{format_id}/best',
        'cookiefile': 'cookies.txt',
        'outtmpl': 'video_%(id)s.%(ext)s',
        'nocheckcertificate': True,
        'merge_output_format': 'mp4',
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'mweb'],
                'po_token': ['web+password'],
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Bot is awake! Send me a YouTube link and I'll ask for the quality.")

@bot.message_handler(func=lambda m: "youtube.com" in m.text or "youtu.be" in m.text)
def handle_video_link(message):
    try:
        url = message.text.strip()
        bot.reply_to(message, "Fetching available qualities...")
        
        qualities, video_id = get_available_qualities(url)
        
        if not qualities:
            bot.reply_to(message, "Could not find any standard qualities for this video.")
            return

        # Create buttons
        markup = types.InlineKeyboardMarkup()
        for q in qualities[:5]: # Show top 5 qualities to keep it clean
            # We store the format_id and the URL in the callback data
            # Format: "dl|[format_id]|[url]"
            callback_data = f"dl|{q['format_id']}|{url}"
            btn = types.InlineKeyboardButton(text=f"🎬 {q['height']}p", callback_data=callback_data)
            markup.add(btn)
            
        bot.send_message(message.chat.id, "Select your preferred quality:", reply_markup=markup)
        
    except Exception as e:
        bot.reply_to(message, f"Error fetching qualities: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl|'))
def process_download_selection(call):
    # Extract data from the callback
     format_id, url = call.data.split('|')
    
     bot.edit_message_text("Downloading selected quality... please wait.", call.message.chat.id, call.message.message_id)
     try:
        # This calls your download function
        file_path = download_video(url, format_id)
        
        with open(file_path, 'rb') as video:
            bot.send_video(call.message.chat.id, video)
            
        os.remove(file_path) # Important! Cleanup the file
        bot.delete_message(call.message.chat.id, call.message.message_id) # Remove the "Downloading" text
        
     except Exception as e:
        bot.send_message(call.message.chat.id, f"Download failed: {str(e)}")
    
if __name__ == "__main__":
      print("--- BOT STARTED SUCCESSFULLY ---")
      bot.infinity_polling()  