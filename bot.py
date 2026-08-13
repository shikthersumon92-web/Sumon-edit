import os
import telebot
import subprocess
from telebot import types

TOKEN = '8844506424:AAEbzTkcruoF0uN41Is-uS_6Z0pptmDGWI0'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("Upload Video"))
    bot.reply_to(message, "হ্যালো! ভিডিও এডিট করার জন্য নিচে দেওয়া 'Upload Video' বাটনে ক্লিক করুন।", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Upload Video")
def prompt_upload(message):
    bot.reply_to(message, "দয়া করে আপনার ভিডিও ফাইলটি পাঠান।")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        msg = bot.reply_to(message, "ভিডিও ডাউনলোড হচ্ছে, এডিটিং শুরু হচ্ছে...")
        
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_file = "input.mp4"
        output_file = "output.mp4"
        
        with open(input_file, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        # ভিডিও ফিল্টার (ফেস অ্যানিমেশন ইফেক্ট সহ)
        # setpts=1/1.07*PTS দিয়ে ভিডিওর গতি অডিওর সাথে সিঙ্ক করা হয়েছে
        video_filters = (
            "crop=in_w*0.95:in_h*0.95,"
            "eq=brightness=0.05:contrast=1.1:saturation=1.2,"
            "smartblur=1.5:-0.5:2.0:0.5," # ফেস অ্যানিমেশন বা কার্টুন লুক
            "unsharp=5:5:1.5:5:5:0.5,"    # শার্পনেস বাড়িয়ে কার্টুন ভাইব
            "noise=alls=5:allf=t+u,"      # কপিরাইট সুরক্ষা গ্রেইন
            "setpts=1/1.07*PTS"           # ভিডিও স্পিড অডিওর সাথে সিঙ্ক
        )
        
        # অডিও ফিল্টার (এআই ভয়েস ইফেক্ট সহ)
        audio_filters = (
            "highpass=f=200,lowpass=f=3000," 
            "atempo=1.07,"        # অডিওর গতি ১০৭%
            "asetrate=44100*1.07," # পিচ বাড়িয়ে রোবটিক/এআই ভয়েস
            "aresample=44100,"
            "aecho=0.8:0.88:60:0.4"
        )
        
        cmd = [
            'ffmpeg', '-i', input_file,
            '-vf', video_filters,
            '-af', audio_filters,
            '-c:v', 'libx264', '-preset', 'veryfast',
            '-c:a', 'aac', '-y', output_file
        ]
        
        subprocess.run(cmd, check=True)
        
        bot.edit_message_text("এডিটিং সম্পন্ন! ভিডিও পাঠানো হচ্ছে...", message.chat.id, msg.message_id)
        
        with open(output_file, 'rb') as vid:
            bot.send_video(message.chat.id, vid, caption="আপনার এআই অ্যানিমেশন স্টাইল ভিডিও তৈরি!")
            
        os.remove(input_file)
        os.remove(output_file)
        
    except Exception as e:
        bot.reply_to(message, f"দুঃখিত, ফাইলটি অনেক বড় বা অন্য সমস্যা হয়েছে: {str(e)}")

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True)
