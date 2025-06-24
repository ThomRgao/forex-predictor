import asyncio
from telegram import Bot

TOKEN = "7903605151:AAE4KU_poFKWHjLcyxxFI0nlFJXizm8XbFQ"
CHAT_ID = 1155752955
bot = Bot(token=TOKEN)

async def send_signal(signal, price, pair, waktu):
    text = f"📊 *Signal Detected!* ({pair})\n\n💥 Sinyal: *{signal}*\n💵 Harga: {price}\n🕒 Waktu: {waktu}"
    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")

# Misalnya setelah ambil data dari API:
if data["signal"] in ["BUY", "SELL"]:
    asyncio.run(send_signal(data["signal"], data["last_close"], data["symbol"], data["time"]))
