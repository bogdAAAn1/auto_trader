import os
import threading
import webserver  # <-- наш Flask-сервер
from strategy import run_strategy  # функция бота

def start_trading():
    run_strategy()

def start_web():
    webserver.app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    threading.Thread(target=start_trading).start()
    start_web()
