import os
import telebot
import subprocess

# Telegram Bot Token
TOKEN = 8844506424:AAH-UeFYjmchlaPNhT4Rk1vmqmnbGNWAp44
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(bot_message):
    bot.reply_to(bot_message, "Welcome! Send me a video, and I will edit it to be copyright-safe.")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        msg = bot.reply_to(message, "Downloading video, please wait...")
        
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_file = "input.mp4"
        output_file = "output.mp4"
        
        with open(input_file, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        bot.edit_message_text("Applying video crop, mirror, audio adjustments, and watermark...", message.chat.id, msg.message_id)
        
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
        
        bot.edit_message_text("Editing finished! Sending your video...", message.chat.id, msg.message_id)
        
        with open(output_file, 'rb') as vid:
            bot.send_video(message.chat.id, vid, caption="Here is your copyright-safe edited video!")
            
        os.remove(input_file)
        os.remove(output_file)
        
    except Exception as e:
        bot.reply_to(message, f"Sorry, an error occurred: {str(e)}")

if __name__ == '__main__':
    try:
        bot.remove_webhook()
        print("Bot is starting successfully...")
        bot.infinity_polling(skip_pending=True, timeout=90, long_polling_timeout=90)
    except Exception as e:
        print(f"Polling error: {e}")
