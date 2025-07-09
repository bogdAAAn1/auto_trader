import time
from strategy import run_strategy

if __name__ == "__main__":
    print("🚀 Запуск EMA-бота...")
    while True:
        run_strategy()
        time.sleep(60 * 60)  # Ждём 1 час до следующей свечи
