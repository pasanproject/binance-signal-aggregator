from flask import Flask, render_template, jsonify
import asyncio
from telethon import TelegramClient
import json
from datetime import datetime
import os

app = Flask(__name__)

# Telegram Credentials (ඔබේ .env file එකේ දාන්න)
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE = os.getenv('PHONE')
CHANNELS = ["channelusername1", "channelusername2"]  # ඔබේ channels

signals = []  # සියලු signals මෙතන save වෙනවා

@app.route('/')
def home():
    return render_template('index.html', signals=signals[-50:])  # අලුත්ම 50

@app.route('/signals')
def get_signals():
    return jsonify(signals[-100:])

# Telegram Listener (Background එකක run වෙනවා)
async def listen_telegram():
    client = TelegramClient('session', API_ID, API_HASH)
    await client.start(phone=PHONE)
    
    @client.on(events.NewMessage(chats=CHANNELS))
    async def new_message(event):
        msg = event.message.message
        if any(keyword in msg.lower() for keyword in ['buy', 'sell', 'long', 'short', 'tp', 'sl']):
            signal = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "channel": event.chat.title,
                "message": msg[:500],
                "raw": msg
            }
            signals.append(signal)
            print(f"New Signal: {signal['time']}")
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Background එකේ Telegram listener run කරන්න
    loop = asyncio.get_event_loop()
    loop.create_task(listen_telegram())
    app.run(host='0.0.0.0', port=5000, debug=True)