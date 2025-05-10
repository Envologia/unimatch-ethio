# Uni Match Ethiopia Bot

A Telegram bot for connecting university students in Ethiopia. The bot helps students find matches based on their preferences, share anonymous confessions, and interact with the community.

## Features

- **Profile Management**
  - Create and edit profiles
  - Set preferences for matches
  - Upload profile photos
  - Manage personal information

- **Matching System**
  - Find matches based on preferences
  - View and manage matches
  - Mutual matching system
  - Match notifications

- **Confession System**
  - Share anonymous confessions
  - View recent confessions
  - Manage your confessions
  - Moderation system

- **Channel Integration**
  - Official channel posting
  - Confession channel
  - Membership verification
  - Admin controls

- **Reporting System**
  - Report users
  - Admin moderation
  - Status tracking
  - User notifications

## Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Telegram Bot Token

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/uni-match-ethiopia.git
   cd uni-match-ethiopia
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```env
   # Bot Configuration
   BOT_TOKEN=your_bot_token
   BOT_USERNAME=@your_bot_username

   # Database Configuration
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname

   # Redis Configuration
   REDIS_URL=redis://localhost:6379/0

   # Channel Configuration
   OFFICIAL_CHANNEL=@your_official_channel
   CONFESSION_CHANNEL=@your_confession_channel

   # Admin Configuration
   ADMIN_IDS=123456789,987654321

   # Rate Limiting
   DAILY_MATCH_LIMIT=10
   DAILY_CONFESSION_LIMIT=3
   MATCH_COOLDOWN=3600

   # Content Limits
   MAX_CONFESSION_LENGTH=1000
   MAX_BIO_LENGTH=500
   MAX_HOBBIES_LENGTH=200

   # Age Restrictions
   MIN_AGE=18
   MAX_AGE=100

   # Logging
   LOG_LEVEL=INFO

   # Feature Flags
   ENABLE_MATCHING=true
   ENABLE_CONFESSIONS=true
   ENABLE_REPORTS=true
   ENABLE_CHANNEL_POSTS=true
   ```

5. Initialize database:
   ```bash
   alembic upgrade head
   ```

## Usage

1. Start the bot:
   ```bash
   python main.py
   ```

2. For production deployment:
   ```bash
   gunicorn web:app --worker-class aiohttp.worker.GunicornWebWorker --bind 0.0.0.0:$PORT
   ```

## Development

1. Run tests:
   ```bash
   pytest
   ```

2. Format code:
   ```bash
   black .
   isort .
   ```

3. Check code quality:
   ```bash
   flake8
   mypy .
   ```

4. Generate documentation:
   ```bash
   sphinx-build -b html docs/ docs/_build/html
   ```

## Project Structure

```
uni-match-ethiopia/
├── alembic/              # Database migrations
├── database/            # Database models and connection
├── handlers/            # Bot handlers
│   ├── channel.py      # Channel handlers
│   ├── confession.py   # Confession handlers
│   ├── keyboards.py    # Keyboard layouts
│   ├── match.py        # Match handlers
│   ├── profile.py      # Profile handlers
│   ├── report.py       # Report handlers
│   └── states.py       # State definitions
├── middleware/          # Bot middleware
│   ├── database.py     # Database middleware
│   ├── error_handler.py # Error handling
│   └── rate_limit.py   # Rate limiting
├── tests/              # Test files
├── .env               # Environment variables
├── .gitignore        # Git ignore file
├── alembic.ini       # Alembic configuration
├── config.py         # Configuration file
├── main.py           # Main bot file
├── Procfile          # Heroku configuration
├── README.md         # This file
├── requirements.txt  # Dependencies
└── web.py            # Web server
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments

- [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot Framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL Toolkit and ORM
- [Redis](https://redis.io/) - In-Memory Data Structure Store
- [Alembic](https://alembic.sqlalchemy.org/) - Database Migration Tool 