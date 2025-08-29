# Instagram Utility Bot

A powerful Instagram Direct Message automation bot built with Python and the `instagrapi` library. This bot helps manage group chats by automating welcome messages, member mentions, and admin commands.

## 🚀 Features

- **Auto Welcome Messages**: Automatically welcomes new members with customizable messages
- **Admin Commands**: Supports various admin-only commands for group management
- **Message Tracking**: Prevents duplicate command execution with message ID tracking
- **2FA Support**: Full two-factor authentication support with backup codes
- **Session Persistence**: Maintains login sessions for continuous operation
- **Multi-Group Support**: Manages multiple group chats simultaneously

## 📋 Available Commands

- `/mentionall` - Mentions all members in the group (admin only)
- `/setwelcome <message>` - Sets custom welcome message (use `{}` for username placeholder)
- `/getwelcome` - Shows current welcome message
- `/updateadmins` - Refreshes admin list
- `/help` - Displays available commands

## 🛠️ Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd insta-utility-bot
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file with your Instagram credentials:
   ```
   IG_USERNAME=your_instagram_username
   IG_PASSWORD=your_instagram_password
   IG_BACKUP_CODES=backup_code_1,backup_code_2,backup_code_3  # Optional for 2FA
   ```

## 🚦 Usage

Run the bot:

```bash
python bot.py
```

The bot will:

- Log in to your Instagram account
- Load or create session data
- Start monitoring your group chats
- Respond to commands and welcome new members

## 🔒 Security Notes

- **Never commit sensitive files** to version control
- The `.gitignore` file excludes: `.env`, `session.json`, `bot_data.json`
- Backup codes are stored securely in environment variables
- Session data is encrypted and stored locally

## 🌐 Hosting Options

For 24/7 operation, consider these free hosting platforms:

- **PythonAnywhere** - Free tier with continuous execution
- **Heroku** - Free dynos with some limitations
- **Replit** - Always-on option available
- **Google Cloud Run** - Generous free tier
- **AWS Free Tier** - EC2 instances for 12 months
- **Railway** - Developer-friendly free tier

## 📁 Project Structure

```
insta-utility-bot/
├── bot.py              # Main bot application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── .gitignore         # Git ignore rules
├── TODO.md            # Development progress
└── (generated files)
    ├── session.json   # Instagram session data
    └── bot_data.json  # Bot configuration data
```

## ⚠️ Important Notes

- Use this bot responsibly and in compliance with Instagram's Terms of Service
- The bot may require manual intervention for 2FA setup initially
- Monitor the bot's activity to ensure proper functioning
- Keep your backup codes secure and update them as needed

## 🐛 Troubleshooting

**Common Issues:**

- **Login failures**: Check credentials and 2FA settings
- **Session errors**: Delete `session.json` to force fresh login
- **Command not working**: Ensure you're an admin in the group

**Error Messages:**

- "Two-factor authentication required" - Provide backup codes in `.env`
- "Invalid credentials" - Verify username/password in `.env`

## 📄 License

This project is provided as-is for educational and personal use. Users are responsible for complying with Instagram's terms of service.

## 👨‍💻 Author

Developed by onlyrohanss

---

**Disclaimer**: This bot is for educational purposes. Use responsibly and at your own risk. The developers are not responsible for any account restrictions or violations of terms of service.
