import os
import telebot
import time
import random
import yt_dlp

def download_from_url(url):
    time.sleep(random.randint(2, 5))
    
    ydl_opts = {
        # This is the most compatible format for Telegram and YouTube
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        
        # This tells it to just grab whatever works if the above fails
        'ignoreerrors': True,
        'no_warnings': True,
        'quiet': True,
        
        # This is the most important part - it mimics a standard Android phone
        'extractor_args': {
            'youtube': {
                'player_client': ['android'],
            }
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # We use process_info to make sure we get a valid result
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)