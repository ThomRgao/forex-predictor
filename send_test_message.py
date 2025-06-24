def send_telegram_message(text, image_buf=None):
    import asyncio
    from telegram import Bot, InputFile

    async def _send():
        bot = Bot(token="7903605151:AAE4KU_poFKWHjLcyxxFI0nlFJXizm8XbFQ")
        await bot.send_message(chat_id=1155752955, text=text)

    print("[INFO] Mengirim sinyal Telegram...")
    asyncio.run(_send())
