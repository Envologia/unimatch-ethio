import asyncio
from aiohttp import web
import os
from config import BOT_TOKEN
from main import bot, dp, setup_bot

async def webhook(request):
    """Handle incoming webhook requests."""
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()

async def health_check(request):
    """Health check endpoint."""
    return web.Response(text="Bot is running!")

async def on_startup(app):
    """Set up webhook and bot on startup."""
    # Set up webhook
    webhook_url = f"https://{app['domain']}/webhook"
    await bot.set_webhook(webhook_url)
    
    # Initialize bot
    await setup_bot()
    app['bot_task'] = asyncio.create_task(dp.start_polling(bot))

async def on_shutdown(app):
    """Clean up on shutdown."""
    # Stop the bot
    if 'bot_task' in app:
        app['bot_task'].cancel()
        try:
            await app['bot_task']
        except asyncio.CancelledError:
            pass
    
    # Delete webhook
    await bot.delete_webhook()
    await bot.session.close()

def create_app(domain):
    """Create the web application."""
    app = web.Application()
    app['domain'] = domain
    
    # Add routes
    app.router.add_post('/webhook', webhook)
    app.router.add_get('/health', health_check)
    
    # Add startup and shutdown handlers
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    return app

# Initialize app with domain from environment variable
app = create_app(os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost')) 