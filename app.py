from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv
from datetime import datetime
import pytz
import os
import json
import telegram
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO

# === Load variabel dari .env ===
load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN', '7903605151:AAE4KU_poFKWHjLcyxxFI0nlFJXizm8XbFQ')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '1155752955')

app = Flask(__name__)
CORS(app)

API_KEY = '45ff41ffa04e40d2aedefb814f8ddec3'
BASE_URL = 'https://api.twelvedata.com/time_series'

# === Fungsi Kirim Telegram ===
def send_telegram_message(text, image_buf=None):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ BOT_TOKEN atau CHAT_ID belum diatur.")
        return
    try:
        bot = telegram.Bot(token=BOT_TOKEN)
        print("Mengirim pesan Telegram...")
        # Kirim hanya pesan teks, abaikan image_buf
        bot.send_message(chat_id=CHAT_ID, text=text)
        print("✅ Pesan berhasil dikirim.")
    except Exception as e:
        print("❌ Telegram Error:", e)

# === Simpan histori ke file ===
def save_signal_history(data):
    path = 'signal_history.json'
    history = []
    if os.path.exists(path):
        with open(path, 'r') as f:
            try:
                history = json.load(f)
            except:
                pass
    history.append(data)
    with open(path, 'w') as f:
        json.dump(history[-100:], f, indent=2)

# === Generate grafik harga ===
def generate_chart_image(history, signal_text=""):
    df = pd.DataFrame(history)
    df['time'] = pd.to_datetime(df['time'])
    plt.figure(figsize=(10, 4))
    plt.plot(df['time'], df['close'], label='Harga Penutupan', color='blue', linewidth=2)
    plt.title(f'Grafik Harga\n{signal_text}')
    plt.xlabel('Waktu')
    plt.ylabel('Harga')
    plt.grid(True)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

# === EMA calculation ===
def ema(data, period):
    k = 2 / (period + 1)
    ema_values = []
    for i in range(len(data)):
        if i < period - 1:
            ema_values.append(None)
        elif i == period - 1:
            sma = sum(data[:period]) / period
            ema_values.append(sma)
        else:
            ema_values.append(data[i] * k + ema_values[i - 1] * (1 - k))
    return ema_values

# === RSI calculation ===
def rsi(prices, period=14):
    if len(prices) < period + 1:
        return [None] * len(prices)
    deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    gains = [max(delta, 0) for delta in deltas]
    losses = [abs(min(delta, 0)) for delta in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    rsis = [None] * period
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsis.append(100.0 if avg_loss == 0 else 100 - (100 / (1 + rs)))
    for i in range(period + 1, len(prices)):
        gain = gains[i - 1]
        loss = losses[i - 1]
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsis.append(100.0 if avg_loss == 0 else 100 - (100 / (1 + rs)))
    while len(rsis) < len(prices):
        rsis.append(None)
    return rsis

# === Endpoint utama ===
@app.route('/predict')
def predict():
    symbol = request.args.get('symbol', 'EUR/USD').upper()
    interval = '1min'

    params = {
        'symbol': symbol,
        'interval': interval,
        'apikey': API_KEY,
        'outputsize': 100
    }

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
    except Exception as e:
        return jsonify({'error': f'Gagal mengambil data: {str(e)}'}), 500

    if 'values' not in data:
        return jsonify({'error': data.get('message', 'Data tidak tersedia')}), 500

    values = list(reversed(data['values']))
    if len(values) < 20:
        return jsonify({'error': 'Data tidak cukup'}), 500

    closes = [float(item['close']) for item in values]
    latest = values[-1]
    latest_close = float(latest['close'])
    latest_time_utc = datetime.strptime(latest['datetime'], '%Y-%m-%d %H:%M:%S')
    wib = pytz.timezone('Asia/Jakarta')
    latest_time_local = pytz.utc.localize(latest_time_utc).astimezone(wib).strftime('%Y-%m-%d %H:%M:%S')

    ema5_list = ema(closes, 5)
    ema20_list = ema(closes, 20)

    ema_short = ema5_list[-1]
    ema_long = ema20_list[-1]

    rsi14 = rsi(closes, 14)
    rsi_latest = rsi14[-1] if rsi14[-1] is not None else 0

    # === Logika sinyal ===
    if ema_short and ema_long:
        if ema_short > ema_long and latest_close > ema_short:
            signal = "BUY"
        elif ema_short < ema_long and latest_close < ema_short:
            signal = "SELL"
        else:
            signal = "HOLD"
    else:
        signal = "HOLD"

    print(f"DEBUG: EMA5={ema_short}, EMA20={ema_long}, Harga={latest_close}, Sinyal={signal}")

    trend_strength = round(abs(ema_short - ema_long) / ema_long * 100, 2) if ema_long else 0

    history = [
        {"time": item["datetime"], "close": float(item["close"])}
        for item in values
    ]

    # Kirim pesan Telegram (tanpa gambar)
    message = (
        f"📈 [{symbol}]\n"
        f"Sinyal: {signal}\n"
        f"Harga: {latest_close}\n"
        f"RSI: {round(rsi_latest, 2)}\n"
        f"Kekuatan Tren: {trend_strength}%\n"
        f"Waktu: {latest_time_local}"
    )
    send_telegram_message(message)

    save_signal_history({
        'symbol': symbol,
        'time': latest_time_local,
        'close': latest_close,
        'signal': signal
    })

    return jsonify({
        'symbol': symbol,
        'time': latest_time_local,
        'last_close': latest_close,
        'ema_short': ema_short,
        'ema_long': ema_long,
        'rsi14': rsi_latest,
        'signal': signal,
        'trend_strength': trend_strength,
        'history': history
    })

if __name__ == '__main__':
    send_telegram_message("Halo dari bot prediksi Forex!")
    app.run(debug=True)
