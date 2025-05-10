import os
from dotenv import load_dotenv
import logging
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Channel Configuration
OFFICIAL_CHANNEL = os.getenv("OFFICIAL_CHANNEL")
CONFESSION_CHANNEL = os.getenv("CONFESSION_CHANNEL")
if not OFFICIAL_CHANNEL or not CONFESSION_CHANNEL:
    raise ValueError("Channel environment variables are not set")

# Admin Configuration
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]

# Content Limits
MAX_CONFESSION_LENGTH = 1000
MAX_BIO_LENGTH = 500
MAX_HOBBIES_LENGTH = 200

# Age Restrictions
MIN_AGE = 18
MAX_AGE = 30

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Webhook Configuration
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}" if WEBHOOK_HOST else None

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Cache Configuration
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour

# Security Configuration
ALLOWED_UPDATES = ["message", "callback_query", "my_chat_member"]
MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", "100"))

# Feature Flags
ENABLE_WEBHOOK = bool(os.getenv("ENABLE_WEBHOOK", "False"))
ENABLE_LOGGING = bool(os.getenv("ENABLE_LOGGING", "True"))
ENABLE_METRICS = bool(os.getenv("ENABLE_METRICS", "False"))
ENABLE_MATCHING = bool(os.getenv("ENABLE_MATCHING", "True"))
ENABLE_CONFESSIONS = bool(os.getenv("ENABLE_CONFESSIONS", "True"))
ENABLE_REPORTS = bool(os.getenv("ENABLE_REPORTS", "True"))
ENABLE_CHANNEL_POSTS = bool(os.getenv("ENABLE_CHANNEL_POSTS", "True"))

# Message Templates
MESSAGES = {
    "welcome": """Welcome to Uni Match Ethiopia! 🎓

I'm here to help you connect with other university students in Ethiopia. Here's what you can do:

1. Create your profile 📝
2. Find matches based on your preferences 💕
3. Share anonymous confessions 🎭
4. Join our community channels 📢

To get started, use /profile to create your profile.

Need help? Use /help to see all available commands.""",
    
    "help": """Here are all the available commands:

Profile Commands:
/profile - Create or view your profile
/edit_profile - Edit your profile
/delete_profile - Delete your profile

Matching Commands:
/match - Start matching with other users
/matches - View your matches
/unmatch - Unmatch with a user

Confession Commands:
/confess - Share an anonymous confession
/my_confessions - View your confessions
/confessions - View recent confessions

Channel Commands:
/verify - Verify channel membership
/post - Post to official channel (admin only)

Other Commands:
/report - Report a user
/help - Show this help message
/cancel - Cancel current operation""",
    
    "error": "An error occurred. Please try again later.",
    
    "validation": {
        "age": "Age must be between 18 and 30.",
        "bio": f"Bio must be between 1 and {MAX_BIO_LENGTH} characters.",
        "hobbies": f"Hobbies must be between 1 and {MAX_HOBBIES_LENGTH} characters.",
        "confession": f"Confession must be between 1 and {MAX_CONFESSION_LENGTH} characters."
    }
}

# Error Messages
ERROR_MESSAGES = {
    "database_error": "Database error occurred. Please try again later.",
    "validation_error": "Invalid input. Please check your input and try again.",
    "permission_error": "You don't have permission to perform this action.",
    "channel_error": "Error verifying channel membership. Please try again later.",
    "match_error": "Error processing match. Please try again later.",
    "confession_error": "Error processing confession. Please try again later.",
    "server_error": "Server error occurred. Please try again later."
}

def validate_config() -> None:
    """Validate configuration settings."""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is required")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is required")
    if not OFFICIAL_CHANNEL or not CONFESSION_CHANNEL:
        raise ValueError("Channel IDs are required")
    if not ADMIN_IDS:
        raise ValueError("At least one admin ID is required")
    if MIN_AGE < 18 or MAX_AGE > 30:
        raise ValueError("Age limits must be between 18 and 30")
    if MAX_CONFESSION_LENGTH < 1 or MAX_BIO_LENGTH < 1 or MAX_HOBBIES_LENGTH < 1:
        raise ValueError("Content length limits must be positive")
    if CACHE_TTL < 0:
        raise ValueError("Cache TTL must be non-negative")
    if MAX_CONNECTIONS < 1:
        raise ValueError("Max connections must be positive")

# Validate configuration on import
validate_config() 