import os
import telebot
import subprocess
from telebot import types

# Railway-র Environment Variables থেকে টোকেন নেওয়া
TOKEN = os.environ.get('BOT_TOKEN')
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
        msg = bot.reply_to(message, "ভিডিও ডাউনলোড হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...")
        
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_file = "input.mp4"
        output_file = "output.mp4"
        
        with open(input_file, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        bot.edit_message_text("এডিটিং চলছে (ক্রপিং, মিরর, কালার কারেকশন ও ওয়াটারমার্ক)...", message.chat.id, msg.message_id)
        
        # কপিরাইট এড়ানোর জন্য প্রয়োজনীয় ফিল্টারসমূহ
        video_filters = (
            "crop=in_w*0.95:in_h*0.95," # ৫% ক্রপ
            "hflip,"                    # হরিজন্টাল মিরর
            "eq=brightness=0.05:contrast=1.1:saturation=1.2," # কালার এডজাস্টমেন্ট
            "drawtext=text='Digital Skill BD':x=(w-text_w)/2:y=h-80:fontsize=30:fontcolor=white@0.5:box=1:boxcolor=black@0.3" # ওয়াটারমার্ক
        )
        
        # অডিও পিচ ও গতি সামান্য পরিবর্তন
        audio_filters = "asetrate=44100*1.05,aresample=44100,atempo=1.05"
        
        cmd = [
            'ffmpeg', '-i', input_file,
            '-vf', video_filters,
            '-af', audio_filters,
            '-c:v', 'libx264', '-preset', 'veryfast',
            '-c:a', 'aac', '-y', output_file
        ]
        
        subprocess.run(cmd, check=True)
        
        bot.edit_message_text("এডিটিং সম্পন্ন! ভিডিওটি পাঠানো হচ্ছে...", message.chat.id, msg.message_id)
        
        with open(output_file, 'rb') as vid:
            bot.send_video(message.chat.id, vid, caption="আপনার কপিরাইট-মুক্ত এডিট করা ভিডিওটি তৈরি!")
            
        # সার্ভার ক্লিন রাখার জন্য ফাইলগুলো ডিলিট করা
        os.remove(input_file)
        os.remove(output_file)
        
    except Exception as e:
        bot.reply_to(message, f"দুঃখিত, একটি সমস্যা হয়েছে: {str(e)}")

if __name__ == '__main__':
    bot.remove_webhook()
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True)
