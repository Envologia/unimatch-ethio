# Uni Match Ethiopia Bot 🤖

A Telegram bot designed to connect Ethiopian university students. The bot helps students create profiles, find matches, and share confessions within the university community.

## Features 🌟

- **Profile Management**
  - Create and edit user profiles
  - Add personal information (age, gender, university, department)
  - Upload profile pictures
  - Add bio and hobbies

- **University Integration**
  - Support for all Ethiopian universities
  - Comprehensive department listings
  - University-specific community features
  - Regular updates for new universities and departments

- **Matching System**
  - Find compatible matches
  - Filter by university and department
  - View detailed profiles

- **Confessions**
  - Share anonymous confessions
  - View and interact with others' confessions
  - University-specific confession channels

## Tech Stack 💻

- Python 3.9+
- aiogram 3.0+ (Telegram Bot Framework)
- SQLAlchemy (Database ORM)
- PostgreSQL (Database)
- aiohttp (Web Server)
- Gunicorn (WSGI Server)

## Prerequisites 📋

- Python 3.9 or higher
- PostgreSQL database
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

## Local Development Setup 🛠️

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/unimatch-ethiopia.git
   cd unimatch-ethiopia
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```
   BOT_TOKEN=your_telegram_bot_token
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

5. **Run the bot locally**
   ```bash
   python main.py
   ```

## Deployment on Render 🚀

1. **Create a new Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository

2. **Configure the service**
   ```
   Name: unimatch
   Environment: Python 3
   Region: Choose closest to your users
   Branch: main
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn web:app --worker-class aiohttp.worker.GunicornWebWorker --bind 0.0.0.0:$PORT
   ```

3. **Add Environment Variables**
   ```
   BOT_TOKEN=your_telegram_bot_token
   DATABASE_URL=your_postgresql_url
   RENDER_EXTERNAL_HOSTNAME=your-app-name.onrender.com
   ```

4. **Create PostgreSQL Database**
   - Create a new PostgreSQL database on Render
   - Copy the database URL to your environment variables

5. **Deploy**
   - Click "Create Web Service"
   - Wait for the build to complete

## Bot Commands 📝

- `/start` - Start the bot and show main menu
- `/profile` - View and edit your profile
- `/matches` - Find potential matches
- `/confessions` - Access confessions feature

## Project Structure 📁

```
unimatch-ethiopia/
├── config.py           # Configuration settings
├── main.py            # Main bot file
├── web.py             # Web server for webhooks
├── requirements.txt   # Project dependencies
├── Procfile          # Deployment configuration
├── runtime.txt       # Python version specification
├── database/
│   ├── models.py     # Database models
│   └── database.py   # Database connection
└── handlers/
    ├── profile.py    # Profile management
    ├── states.py     # FSM states
    └── keyboards.py  # Inline keyboards
```

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support 💬

For support, please:
- Open an issue in the GitHub repository
- Contact the development team
- Join our [Telegram Support Group](https://t.me/UniMatchSupport)

## Acknowledgments 🙏

- [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot Framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL Toolkit and ORM
- [Render](https://render.com/) - Cloud Platform 