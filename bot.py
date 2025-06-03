from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import json
import os
from dotenv import load_dotenv
from utils.content_manager import ContentManager

# بارگذاری متغیرهای محیطی
load_dotenv()

# مدیریت محتوا
content_mgr = ContentManager()
CONTENT_FILE = "content.json"

def start(update: Update, context: CallbackContext):
    try:
        # بارگذاری محتوا
        context.bot_data['content'] = content_mgr.load_content(CONTENT_FILE)
        
        # ایجاد صفحه کلید
        keyboard = [
            ["📚 درس‌ها", "📝 تمرین‌ها"],
            ["🎯 آزمون فصل", "📊 پیشرفت من"]
        ]
        
        update.message.reply_text(
            f"به آموزش فصل مجموعه‌ها خوش آمدید!\n\n"
            f"📌 {context.bot_data['content']['chapter1']['description']}\n\n"
            "لطفاً گزینه مورد نظر را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
    except Exception as e:
        update.message.reply_text("⚠️ خطا در بارگذاری محتوا. لطفاً بعداً تلاش کنید.")
        print(f"Error in start: {e}")

def show_lessons(update: Update, context: CallbackContext):
    try:
        lessons = context.bot_data['content']['chapter1']['lessons']
        
        keyboard = [
            [f"درس ۱: {lessons['1']['title']}"],
            [f"درس ۲: {lessons['2']['title']}"],
            ["🔙 برگشت"]
        ]
        
        update.message.reply_text(
            "فهرست درس‌های این فصل:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    except Exception as e:
        update.message.reply_text("⚠️ خطا در نمایش درس‌ها.")
        print(f"Error in show_lessons: {e}")

def show_lesson(update: Update, context: CallbackContext):
    try:
        lesson_num = update.message.text.split(":")[0][-1]  # استخراج شماره درس
        lesson = context.bot_data['content']['chapter1']['lessons'][lesson_num]
        
        # ارسال متن درس
        update.message.reply_markdown_v2(lesson['text'])
        
        # ارسال رسانه‌ها
        if 'media' in lesson:
            for img in lesson['media']['images']:
                try:
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=open(f'media/images/{img}', 'rb')
                    )
                except FileNotFoundError:
                    update.message.reply_text("⚠️ تصویر یافت نشد.")
        
        # ارسال مثال‌ها
        for example in lesson['examples']:
            update.message.reply_text(
                f"❓ سوال:\n{example['question']}\n\n"
                f"💡 پاسخ:\n{example['solution']}"
            )
    except Exception as e:
        update.message.reply_text("⚠️ خطا در نمایش درس.")
        print(f"Error in show_lesson: {e}")

def main():
    try:
        TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        if not TOKEN:
            raise ValueError("توکن ربات یافت نشد!")
        
        updater = Updater(TOKEN, use_context=True)
        dp = updater.dispatcher
        
        # دستورات
        dp.add_handler(CommandHandler("start", start))
        
        # هندلرها
        dp.add_handler(MessageHandler(Filters.regex(r'^📚 درس‌ها$'), show_lessons))
        dp.add_handler(MessageHandler(Filters.regex(r'^درس \d:'), show_lesson))
        
        # تنظیمات برای Render
        if os.getenv('RENDER'):
            PORT = int(os.environ.get('PORT', 5000))
            updater.start_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=TOKEN,
                webhook_url=f"https://your-service-name.onrender.com/{TOKEN}"
            )
        else:
            updater.start_polling()
            
        updater.idle()
    except Exception as e:
        print(f"خطای اصلی: {e}")

if __name__ == '__main__':
    main()
