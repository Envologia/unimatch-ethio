import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Channel Configuration
MAIN_CHANNEL = "@UniMatchEthiopia"
CONFESSION_CHANNEL = "@UuniMatchConfession"

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///unimatch.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Profile Settings
MIN_AGE = 18
MAX_AGE = 30

# Webhook Settings
WEBHOOK_HOST = os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost')
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"https://{WEBHOOK_HOST}{WEBHOOK_PATH}" 