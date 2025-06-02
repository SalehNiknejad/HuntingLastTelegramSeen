from telethon.sync import TelegramClient
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
target_chat_id = os.getenv("TARGET_CHAT_ID")
check_interval = 4

client = TelegramClient('session_check', api_id, api_hash)
user_status_map = {}
log = []

with open("users.json", "r", encoding="utf-8") as f:
    users_to_monitor = json.load(f)

async def detect_lastsin_multi():
    await client.start()

    for u in users_to_monitor:
        entity = await client.get_entity(u["username"])
        u["entity"] = entity
        user_status_map[entity.id] = None

    while True:
        for u in users_to_monitor:
            entity = u["entity"]
            alias = u["alias"]

            try:
                user = await client.get_entity(entity.id)
                status = user.status

                if status and status != user_status_map[entity.id]:
                    user_status_map[entity.id] = status
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f'📡 [{alias}] در {now}: {status.__class__.__name__}')

                    log_entry = {
                        "time": now,
                        "username": user.username if user.username else str(user.id),
                        "alias": alias,
                        "status": status.__class__.__name__
                    }
                    log.append(log_entry)

                    with open("status_log.json", "w", encoding="utf-8") as f:
                        json.dump(log, f, ensure_ascii=False, indent=2)

                    message = f"🕵️‍♂️ وضعیت جدید برای {alias}:\n\n🕒 {now}\n📶 {status.__class__.__name__}"
                    await client.send_message(target_chat_id, message, silent=u["silent"])

            except Exception as e:
                print(f"❗ خطا در بررسی {alias}: {e}")

        await asyncio.sleep(check_interval)

with client:
    client.loop.run_until_complete(detect_lastsin_multi())
