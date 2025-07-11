import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
import yt_dlp

# Enable logging for debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your actual Telegram user ID
ADMIN_ID = 1717962827

# Track number of videos downloaded
video_download_count = 0

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to the Video Downloader Bot!\nSend a video link to begin downloading.")

# /help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📥 *How to Use This Bot:*\n"
        "Just send a video link (e.g., YouTube, Twitter), and I’ll try to download it for you.\n\n"
        "🔧 *Commands:*\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/stats - Bot usage stats (admin only)\n\n"
        "Bot created by [@RICCHMOND_DR](https://t.me/RICCHMOND_DR)"
    )
    await update.message.reply_markdown(help_text)

# /stats command for admin only
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to view stats.")
        return

    await update.message.reply_text(f"📊 Total videos downloaded: {video_download_count}")

# Handle messages (assume they are video links)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global video_download_count

    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ That doesn't look like a valid URL.")
        return

    await update.message.reply_text("⏳ Downloading video... Please wait.")

    try:
        ydl_opts = {
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "format": "bestvideo+bestaudio/best",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # Send video
        await update.message.reply_video(video=open(file_path, "rb"))
        video_download_count += 1

        # Delete file to save space
        os.remove(file_path)

    except Exception as e:
        logger.error("Error downloading video: %s", str(e))
        await update.message.reply_text("❌ Failed to download video. The link may be unsupported or too large.")

# Main function to start the bot
def main():
    # Read bot token from environment variable
    TOKEN = os.environ.get("BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats))

    # Register message handler for video links
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
