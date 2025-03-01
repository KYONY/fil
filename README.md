# Instagram Link Converter Bot

A Telegram bot that automatically converts Instagram links to ddinstagram.com format, which provides Instagram content without requiring login.

## Features

- Automatically detects Instagram links in messages
- Converts both post and reel links to ddinstagram.com format
- Supports multiple user channels
- Daily log rotation with 2-month retention
- Session file management
- Docker containerization with auto-restart functionality

## Prerequisites

- Docker and Docker Compose installed on your server
- Telegram Bot Token (from @BotFather)
- Telegram API credentials (from https://my.telegram.org/apps)

## Setup

1. Clone this repository to your local machine or server:
   ```
   git clone https://github.com/yourusername/instagram-link-converter-bot.git
   cd instagram-link-converter-bot
   ```

2. Create a `.env` file in the project root with the following content:
   ```
   # Telegram API credentials
   # Get these from https://my.telegram.org/apps
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash

   # Telegram Bot Token
   # Get this from @BotFather
   TELEGRAM_BOT_TOKEN="your_bot_token"

   # Optional Instagram credentials (to avoid rate limits)
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_instagram_password

   # User channel configuration
   # Get user ID by sending a message to @userinfobot in Telegram
   USER1_ID=your_telegram_id
   USER1_CHANNEL=your_channel_id_or_name

   # Additional users (optional)
   USER2_ID=another_user_telegram_id
   USER2_CHANNEL=another_channel_id_or_name
   ```

3. Build and start the Docker container:
   ```
   docker-compose up -d
   ```

## Usage

1. Add your bot to the Telegram channel you want to monitor (make sure to give it admin privileges so it can post messages)
2. Share Instagram links in your channel
3. The bot will automatically reply to Instagram links with the ddinstagram.com equivalent

## Maintenance

- Logs are stored in the `logs` directory and rotated daily
- Old logs (older than 2 months) are automatically cleaned up
- The session file is monitored and recreated if it grows too large
- The container is configured to automatically restart if the bot crashes

## Commands

- `/start` - Start the bot and receive a welcome message
- `/help` - Get help information about the bot

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.