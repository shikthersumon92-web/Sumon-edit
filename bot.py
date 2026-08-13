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
        msg = bot.reply_to(message, "ভিডিও ডাউনলোড হচ্ছে, অ্যানিমেশন ও কপিরাইট প্রোটেকশন সহ এডিটিং চলছে...")
        
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_file = "input.mp4"
        output_file = "output.mp4"
        
        with open(input_file, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        # ভিডিও ফিল্টার: ৫০% অ্যানিমেশন এবং ৫০% রিয়েল লুক (Boxblur, Unsharp, Hue ও Noise)
        # setpts দিয়ে ভিডিওর গতি অডিওর সাথে নিখুঁতভাবে সিঙ্ক করা হয়েছে
        video_filters = (
            "crop=in_w*0.90:in_h*0.90,"
            "eq=brightness=0.05:contrast=1.1:saturation=1.3,"
            "boxblur=1.5:1,"               # হালকা ব্লার যা অ্যানিমেশন ভাইব দেয়
            "unsharp=3:3:0.8:3:3:0.4,"    # অবয়ব স্পষ্ট রাখার জন্য শার্পনেস
            "hue=h=15:s=1.2,"             # রঙের টোন পরিবর্তন (রিয়েল + অ্যানিমেশন মিক্স)
            "noise=alls=3:allf=t+u,"      # কপিরাইট এড়ানোর জন্য ডিজিটাল গ্রেইন
            "setpts=1/1.10*PTS"           # ভিডিও স্পিড ১১০%
        )
        
        # অডিও ফিল্টার: এআই ভয়েস ভাইব ও সিঙ্ক ঠিক রাখার জন্য স্পিড ১১০%
        audio_filters = (
            "atempo=1.10,"
            "asetrate=44100*1.05,"
            "aresample=44100,"
            "aecho=0.7:0.7:500:0.2"
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
            bot.send_video(message.chat.id, vid, caption="আপনার অ্যানিমেশন স্টাইল ও কপিরাইট-মুক্ত ভিডিও প্রস্তুত!")
            
        os.remove(input_file)
        os.remove(output_file)
        
    except Exception as e:
        bot.reply_to(message, f"দুঃখিত, ফাইল সাইজ বড় বা অন্য কোনো সমস্যা হয়েছে: {str(e)}")

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True)
