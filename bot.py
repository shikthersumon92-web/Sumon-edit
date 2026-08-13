import os
import telebot
import subprocess
from telebot import types

# Your new Telegram Token
TOKEN = '8844506424:AAH-UeFYjmchlaPNhT4Rk1vmqmnbGNWAp44'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Creating a keyboard button for the user to upload video
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button = types.KeyboardButton("Upload Video")
    markup.add(button)
    
    bot.reply_to(message, "Welcome! Click the button below to upload your video, and I will edit it for you.", reply_markup=markup)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        msg = bot.reply_to(message, "Downloading your video, please wait...")
        
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_file = "input.mp4"
        output_file = "output.mp4"
        
        with open(input_file, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        bot.edit_message_text("Processing video (Cropping, Mirroring, Color Correction & Watermark)...", message.chat.id, msg.message_id)
        
        # FFmpeg filters
        video_filters = (
            "crop=in_w*0.98:in_h*0.98,scale=iw:ih,"
            "hflip,"
            "eq=brightness=0.04:contrast=1.08:saturation=1.15,"
            "drawtext=text='Digital Skill BD':x=(w-text_w)/2:y=h-50:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.4"
        )
        audio_filters = "asetrate=44100*1.03,aresample=44100,atempo=1.02"
        
        cmd = [
            'ffmpeg', '-i', input_file,
            '-vf', video_filters,
            '-af', audio_filters,
            '-y', output_file
        ]
        
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        bot.edit_message_text("Editing complete! Sending video...", message.chat.id, msg.message_id)
        
        with open(output_file, 'rb') as vid:
            bot.send_video(message.chat.id, vid, caption="Here is your copyright-safe edited video!")
            
        # Cleanup
        os.remove(input_file)
        os.remove(output_file)
        
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

@bot.message_handler(func=lambda message: message.text == "Upload Video")
def prompt_upload(message):
    bot.reply_to(message, "Please send me the video file now.")

if __name__ == '__main__':
    try:
        bot.remove_webhook()
        print("Bot is running...")
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"Polling error: {e}")
