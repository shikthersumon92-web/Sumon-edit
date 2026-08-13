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
        msg = bot.reply_to(message, "ভিডিও ডাউনলোড হচ্ছে, স্বাভাবিক গতি ও অ্যানিমেশন স্টাইলে এডিটিং চলছে...")
        
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_file = "input.mp4"
        output_file = "output.mp4"
        
        with open(input_file, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        # স্পিড খুব কম বাড়িয়ে (১.০৪ গুণ) ভিডিও ও অডিওর সিঙ্ক ঠিক রাখা হয়েছে
        # boxblur এবং unsharp দিয়ে হালকা অ্যানিমেশন বা কার্টুনিশ লুক আনা হয়েছে
        video_filters = (
            "crop=in_w*0.95:in_h*0.95,"
            "eq=brightness=0.04:contrast=1.05:saturation=1.15,"
            "boxblur=1:0.8,"              # হালকা ব্লার (অ্যানিমেশন ভাইব)
            "unsharp=3:3:0.6:3:3:0.3,"   # শার্পনেস ঠিক রাখা
            "hue=h=5:s=1.1,"             # কালার শিফট
            "setpts=1/1.04*PTS"          # স্পিড মাত্র ৪% বাড়ানো হলো যাতে স্বাভাবিক থাকে
        )
        
        # অডিও ফিল্টার যাতে ভিডিওর গতির (১.০৪) সাথে পারফেক্টলি মিলে যায়
        audio_filters = (
            "atempo=1.04,"               # অডিও স্পিড ৪% বৃদ্ধি
            "asetrate=44100*1.02,"       # পিচ সামান্য পরিবর্তন (এআই ভয়েস ভাব)
            "aresample=44100"
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
            bot.send_video(message.chat.id, vid, caption="আপনার এডিট করা ভিডিও প্রস্তুত!")
            
        os.remove(input_file)
        os.remove(output_file)
        
    except Exception as e:
        bot.reply_to(message, f"দুঃখিত, একটি সমস্যা হয়েছে: {str(e)}")

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True)
