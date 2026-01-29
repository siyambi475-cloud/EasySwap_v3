from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7851734819:AAFvcCDz25Gkkg86V6GRqvnSj7DpsUN6t8U"
WEB_APP_URL = "https://easyswap-v3.onrender.com" 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚀 Open EasySwap Game", web_app=WebAppInfo(url=WEB_APP_URL))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to EasySwap! Tap below to start earning coins.", 
        reply_markup=reply_markup
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

if __name__ == '__main__':
    app.run_polling()
