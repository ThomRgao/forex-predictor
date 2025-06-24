import time
import requests

def loop_prediction():
    while True:
        try:
            # Ganti dengan pair yang kamu mau
            symbol = "EUR/USD"
            url = f"http://127.0.0.1:5000/predict?symbol={symbol}"
            response = requests.get(url)
            print(f"[OK] Dikirim: {response.json()['signal']} | {response.json()['time']}")
        except Exception as e:
            print("[ERROR]", e)
        time.sleep(60)  # tunggu 60 detik

if __name__ == "__main__":
    loop_prediction()
