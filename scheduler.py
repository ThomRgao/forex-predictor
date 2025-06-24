import time
import requests

while True:
    try:
        print("[⏱️] Memanggil prediksi...")
        r = requests.get("http://localhost:5000/predict?symbol=EUR/USD")
        print("[✅] Status:", r.status_code)
        print("[📊] Response:", r.json())
    except Exception as e:
        print("[⚠️] Gagal memanggil prediksi:", e)
    time.sleep(60)
