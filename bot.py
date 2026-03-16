import time
import telebot
import random
import os
import yt_dlp

def download_from_url(url):
    # This adds a random 3-7 second delay before starting
    # It stops YouTube from seeing a "pattern" of bot activity
    time.sleep(random.randint(3, 7))
    cookies_content = os.getenv("COOKIES")
    if cookies_content:
     with open("cookies.txt", "w") as f:
        f.write(cookies_content)

    ydl_opts = {
        # This checks if the Railway variable exists and creates the file for the bot

        'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
        'cookiefile': 'cookies.txt',
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
    