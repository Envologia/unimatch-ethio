web: gunicorn web:app --worker-class aiohttp.worker.GunicornWebWorker --bind 0.0.0.0:$PORT
worker: python main.py 