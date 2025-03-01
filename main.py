import os
import logging
import asyncio
import re
import time
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient, events

# Load environment variables
load_dotenv()

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging with daily rotation and retention for 2 months
log_file = logs_dir / f"bot_{datetime.now().strftime('%Y-%m-%d')}.log"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# File handler with daily rotation
file_handler = TimedRotatingFileHandler(
    log_file,
    when="midnight",
    interval=1,
    backupCount=60,  # Keep logs for 60 days (2 months)
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)


# Clean up old log files (older than 2 months)
def cleanup_old_logs():
    two_months_ago = datetime.now() - timedelta(days=60)
    for log_file in logs_dir.glob("bot_*.log"):
        try:
            # Extract date from filename
            file_date_str = log_file.name.replace("bot_", "").replace(".log", "")
            file_date = datetime.strptime(file_date_str, "%Y-%m-%d")

            # Remove file if older than 2 months
            if file_date < two_months_ago:
                os.remove(log_file)
                print(f"Removed old log file: {log_file}")
        except Exception as e:
            print(f"Error processing log file {log_file}: {e}")


# Telegram API credentials
API_ID = int(os.environ.get("TELEGRAM_API_ID"))
API_HASH = os.environ.get("TELEGRAM_API_HASH")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# User channel mapping
USER1_CHANNEL = os.environ.get("USER1_CHANNEL")
if USER1_CHANNEL and USER1_CHANNEL.startswith('-100'):
    USER1_CHANNEL = int(USER1_CHANNEL)  # Convert to integer if numeric channel ID

# Create session directory if it doesn't exist
session_dir = Path("tg_bot_session")
session_dir.mkdir(exist_ok=True)

# Manage session file size (monitor and recreate if too large)
SESSION_FILE = session_dir / "instagram_converter_session.session"
MAX_SESSION_SIZE_MB = 10  # Maximum session file size in MB


def check_session_file():
    """Check session file size and recreate if too large"""
    try:
        if os.path.exists(SESSION_FILE):
            size_mb = os.path.getsize(SESSION_FILE) / (1024 * 1024)
            if size_mb > MAX_SESSION_SIZE_MB:
                logger.warning(f"Session file too large ({size_mb:.2f} MB), recreating")
                # Backup old session file
                backup_path = SESSION_FILE.with_suffix(f".session.bak.{int(time.time())}")
                os.rename(SESSION_FILE, backup_path)
                logger.info(f"Backed up old session to {backup_path}")
                return True  # Session was recreated
    except Exception as e:
        logger.error(f"Error checking session file: {e}")
    return False


async def main():
    # Clean up old logs
    cleanup_old_logs()

    # Check session file
    session_recreated = check_session_file()

    # Startup message
    print("Starting Instagram Link Converter Bot...")
    logger.info("Bot starting with the following configuration:")
    logger.info(f"API_ID: {API_ID}")
    logger.info(f"Channel: {USER1_CHANNEL}")

    # Create the client
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

    # Handler for /start command
    @client.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        user_id = event.sender_id
        logger.info(f"Received /start from user {user_id}")
        print(f"Received /start from user {user_id}")
        await event.respond(
            "👋 Welcome to Instagram Link Converter!\n\n"
            "I will convert Instagram links to ddinstagram.com format."
        )

    # Handler for /help command
    @client.on(events.NewMessage(pattern='/help'))
    async def help_handler(event):
        user_id = event.sender_id
        logger.info(f"Received /help from user {user_id}")
        print(f"Received /help from user {user_id}")
        await event.respond(
            "📚 Instagram Link Converter Help:\n\n"
            "I automatically convert Instagram links to ddinstagram.com format.\n\n"
            "Just add me to your channel as an admin, and I'll reply to any Instagram links with a converted link."
        )

    # Instagram link handler
    @client.on(events.NewMessage(pattern=r'https://(www\.)?instagram\.com/(p|reel)/.*'))
    async def instagram_link_handler(event):
        chat_id = event.chat_id
        user_id = event.sender_id
        instagram_url = event.text

        logger.info(f"Instagram link detected: {instagram_url} in chat {chat_id}")
        print(f"Instagram link detected: {instagram_url} in chat {chat_id}")

        # Process the Instagram URL
        # Extract content type (post/reel) and shortcode
        shortcode_match = re.search(r'instagram\.com/p/([^/?]+)', instagram_url)
        reel_match = re.search(r'instagram\.com/reel/([^/?]+)', instagram_url)

        if shortcode_match:
            shortcode = shortcode_match.group(1)
            content_type = "p"  # post
        elif reel_match:
            shortcode = reel_match.group(1)
            content_type = "reel"  # reel
        else:
            logger.error(f"Invalid Instagram URL: {instagram_url}")
            return

        # Create ddinstagram URL
        ddinstagram_url = f"https://www.ddinstagram.com/{content_type}/{shortcode}/"
        logger.info(f"Generated ddinstagram URL: {ddinstagram_url}")
        print(f"Generated ddinstagram URL: {ddinstagram_url}")

        # Reply with the ddinstagram link
        try:
            await client.send_message(
                entity=chat_id,
                message=ddinstagram_url,
                reply_to=event.message.id
            )
            logger.info(f"Replied with ddinstagram link in chat {chat_id}")
            print(f"Replied with ddinstagram link in chat {chat_id}")
        except Exception as e:
            logger.error(f"Error replying with ddinstagram link: {e}")
            print(f"Error replying with ddinstagram link: {e}")

    # Start the client
    try:
        print("Connecting to Telegram...")
        await client.start(bot_token=BOT_TOKEN)
        me = await client.get_me()
        logger.info(f"Bot connected as @{me.username} (ID: {me.id})")
        print(f"Bot connected as @{me.username} (ID: {me.id})")
        print("Bot is now running. Press Ctrl+C to stop.")

        # Run until disconnected
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Critical error: {e}")
        print(f"Critical error: {e}")


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("Bot stopped manually")
            break
        except Exception as e:
            print(f"Bot crashed with error: {e}")
            print("Restarting in 10 seconds...")
            time.sleep(10)