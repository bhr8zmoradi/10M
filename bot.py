from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import json
import os
from utils.content_manager import ContentManager

# تنظیمات
TOKEN = "YOUR_BOT_TOKEN"
CONTENT_FILE = "content.json"

# مدیریت محتوا
content_mgr = ContentManager()

def start(update: Update, context: CallbackContext):
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

def show_lessons(update: Update, context: CallbackContext):
    lessons = context.bot_data['content']['chapter1']['lessons']
    
    keyboard = [
        [f"درس ۱: {lessons['1']['title']}"],
        [f"درس ۲: {lessons['2']['title']}"],
        ["🔙 برگشت"]
    ]
    
    update.message.reply_text(
        "فهرست درس‌های این فصل:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

def show_lesson(update: Update, context: CallbackContext):
    lesson_num = update.message.text.split(":")[0][-1]  # استخراج شماره درس
    lesson = context.bot_data['content']['chapter1']['lessons'][lesson_num]
    
    # ارسال متن درس
    update.message.reply_markdown_v2(lesson['text'])
    
    # ارسال رسانه‌ها
    if 'media' in lesson:
        for img in lesson['media']['images']:
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=open(f'media/images/{img}', 'rb')
            )
    
    # ارسال مثال‌ها
    for example in lesson['examples']:
        update.message.reply_text(
            f"❓ سوال:\n{example['question']}\n\n"
            f"💡 پاسخ:\n{example['solution']}"
        )

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # دستورات
    dp.add_handler(CommandHandler("start", start))
    
    # هندلرها
    dp.add_handler(MessageHandler(Filters.regex(r'^📚 درس‌ها$'), show_lessons))
    dp.add_handler(MessageHandler(Filters.regex(r'^درس \d:'), show_lesson))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
