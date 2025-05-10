import os
import logging
import ssl
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from prometheus_client import Counter, Histogram
import time

from config import (
    BOT_TOKEN, WEBHOOK_HOST, WEBHOOK_PATH, WEBHOOK_URL,
    HOST, PORT, SSL_CERT, SSL_PRIV, ALLOWED_UPDATES,
    MAX_CONNECTIONS, TIMEOUT, LOG_LEVEL, LOG_FORMAT,
    LOG_DATE_FORMAT
)
from main import setup_bot

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

async def on_startup(app: web.Application):
    """Initialize bot and webhook on startup."""
    try:
        # Get bot and dispatcher from app
        bot: Bot = app["bot"]
        dp: Dispatcher = app["dispatcher"]

        # Set webhook
        if WEBHOOK_URL:
            await bot.set_webhook(
                url=WEBHOOK_URL,
                allowed_updates=ALLOWED_UPDATES,
                max_connections=MAX_CONNECTIONS,
                drop_pending_updates=True
            )
            logger.info(f"Webhook set to {WEBHOOK_URL}")
        else:
            logger.warning("Webhook URL not set, running in polling mode")

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

async def on_shutdown(app: web.Application):
    """Cleanup on shutdown."""
    try:
        # Get bot from app
        bot: Bot = app["bot"]

        # Remove webhook
        if WEBHOOK_URL:
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Webhook removed")

        # Close bot session
        await bot.session.close()
        logger.info("Bot session closed")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        raise

def create_app(bot: Bot, dp: Dispatcher) -> web.Application:
    """Create web application.
    
    Args:
        bot: Bot instance
        dp: Dispatcher instance
        
    Returns:
        Web application instance
    """
    # Create application
    app = web.Application(
        client_max_size=1024**2,  # 1MB
        timeout=TIMEOUT,
        middlewares=[
            metrics_middleware,
            error_middleware
        ]
    )

    # Store bot and dispatcher in app
    app["bot"] = bot
    app["dispatcher"] = dp

    # Add startup and shutdown handlers
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Add webhook handler
    if WEBHOOK_URL:
        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        )
        webhook_handler.register(app, path=WEBHOOK_PATH)

    # Setup dispatcher
    setup_application(app, dp, bot=bot)

    # Add routes
    app.router.add_get('/health', health_check)
    app.router.add_get('/metrics', metrics)
    app.router.add_post('/webhook', webhook)

    return app

def run_app(bot: Bot, dp: Dispatcher):
    """Run web application.
    
    Args:
        bot: Bot instance
        dp: Dispatcher instance
    """
    try:
        # Create application
        app = create_app(bot, dp)

        # Configure SSL if certificates are provided
        ssl_context = None
        if SSL_CERT and SSL_PRIV:
            try:
                ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_context.load_cert_chain(SSL_CERT, SSL_PRIV)
                logger.info("SSL context created successfully")
            except Exception as e:
                logger.error(f"Error creating SSL context: {e}")
                raise

        # Run application
        web.run_app(
            app,
            host=HOST,
            port=PORT,
            ssl_context=ssl_context
        )

    except Exception as e:
        logger.error(f"Error running application: {e}")
        raise

async def health_check(request):
    """Health check endpoint."""
    return web.json_response({
        'status': 'healthy',
        'version': os.getenv('VERSION', '1.0.0')
    })

async def metrics(request):
    """Prometheus metrics endpoint."""
    from prometheus_client import generate_latest
    return web.Response(
        body=generate_latest(),
        content_type='text/plain'
    )

async def webhook(request):
    """Webhook endpoint for Telegram updates."""
    try:
        update = await request.json()
        # Process update here
        return web.json_response({'status': 'ok'})
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return web.json_response(
            {'error': str(e)},
            status=500
        )

@web.middleware
async def metrics_middleware(request, handler):
    """Middleware for collecting metrics."""
    start_time = time.time()
    try:
        response = await handler(request)
        status = response.status
    except Exception as e:
        status = 500
        raise
    finally:
        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.path,
            status=status
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.path
        ).observe(duration)
    return response

@web.middleware
async def error_middleware(request, handler):
    """Middleware for error handling."""
    try:
        return await handler(request)
    except web.HTTPException as e:
        return web.json_response(
            {'error': e.reason},
            status=e.status
        )
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return web.json_response(
            {'error': 'Internal server error'},
            status=500
        )

if __name__ == "__main__":
    # Create bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Run application
    run_app(bot, dp) 