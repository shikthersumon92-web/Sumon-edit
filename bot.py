import os
import telebot
import subprocess

# আপনার নতুন টেলিগ্রাম টোকেন
TOKEN = '8844506424:AAH-UeFYjmchlaPNhT4Rk1vmqmnbGNWAp44'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(bot_message):
    bot.reply_to(bot_message, "স্বাগতম! আমাকে একটি ভিডিও দিন, আমি ক্রপ, মিরর, কালার ও ভয়েস চেঞ্জ করে কপিরাইট সেফ এডিট করে দিচ্ছি।")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        msg = bot.reply_to(message, "ভিডিও ডাউনলোড হচ্ছে, দয়া করে অপেক্ষা করুন...")
        
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_file = "input.mp4"
        output_file = "output.mp4"
        
        with open(input_file, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        bot.edit_message_text("ভিডিওতে ক্রপ, মিরর, কালার কারেকশন এবং ওয়াটারমার্ক যুক্ত করা হচ্ছে...", message.chat.id, msg.message_id)
        
        # ভিডিও ফিল্টার (ক্রপ, মিরর, কালার অ্যাডজাস্টমেন্ট ও টেক্সট ওয়াটারমার্ক)
        video_filters = (
            "crop=in_w*0.98:in_h*0.98,scale=iw:ih,"
            "hflip,"
            "eq=brightness=0.04:contrast=1.08:saturation=1.15,"
            "drawtext=text='Digital Skill BD':x=(w-text_w)/2:y=h-50:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.4"
        )
        
        # অডিও ফিল্টার (পিচ ও স্পিড পরিবর্তন)
        audio_filters = "asetrate=44100*1.03,aresample=44100,atempo=1.02"
        
        cmd = [
            'ffmpeg', '-i', input_file,
            '-vf', video_filters,
            '-af', audio_filters,
            '-y', output_file
        ]
        
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        bot.edit_message_text("এডিট শেষ! ভিডিও পাঠানো হচ্ছে...", message.chat.id, msg.message_id)
        
        with open(output_file, 'rb') as vid:
            bot.send_video(message.chat.id, vid, caption="আপনার কপিরাইট সেফ এডিটেড ভিডিও প্রস্তুত!")
            
        # ফাইল ক্লিনআপ
        os.remove(input_file)
        os.remove(output_file)
        
    except Exception as e:
        bot.reply_to(message, f"দুঃখিত, একটি সমস্যা হয়েছে: {str(e)}")

if __name__ == '__main__':
    try:
        bot.remove_webhook()
        print("বট সফলভাবে চালু হচ্ছে...")
        bot.infinity_polling(skip_pending=True, timeout=90, long_polling_timeout=90)
    except Exception as e:
        print(f"Polling error: {e}")
