from telethon import TelegramClient, events
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
import os
from utils import parse_status_log_file

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
target_chat_id = os.getenv("TARGET_CHAT_ID")
check_interval = 8
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")



client = TelegramClient('session_check', api_id, api_hash)
user_status_map = {}
log = []

if os.path.exists("status_log.json"):
    with open("status_log.json", "r", encoding="utf-8") as f:
        try:
            log = json.load(f)
        except json.JSONDecodeError:
            log = []

with open("users.json", "r", encoding="utf-8") as f:
    users_to_monitor = json.load(f)

running_event = asyncio.Event()
running_event.set()

async def detect_lastsin_multi():
    await client.start()

    for u in users_to_monitor:
        try:
            username_or_id = u["username"]
            entity = await client.get_entity(username_or_id)
            u["entity"] = entity
            user_status_map.setdefault(entity.id, None)
        except Exception as e:
            print(f"❗ خطا در بارگذاری entity برای {u.get('alias', '?')}: {e}")

    while True:
        await running_event.wait()

        if not client.is_connected():
            print("🔌 کلاینت قطع شده، اتصال مجدد...")
            await client.connect()

        for u in users_to_monitor:
            try:
                entity = u["entity"]
                alias = u["alias"]

                user = await client.get_entity(entity.id)
                status = user.status

                if status and status != user_status_map.get(entity.id):
                    user_status_map[entity.id] = status
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    status_name = status.__class__.__name__
                    translated_status = status_translations.get(status_name, status_name)

                    log_entry = {
                        "time": now,
                        "username": user.username if user.username else str(user.id),
                        "alias": alias,
                        "status": status_name
                    }
                    log.append(log_entry)

                    with open("status_log.json", "w", encoding="utf-8") as f:
                        json.dump(log, f, indent=2, ensure_ascii=False)

                    message = f"🕵️‍♂️ وضعیت جدید برای {alias}:\n\n🕒 {now}\n📶 {translated_status}"
                    await client.send_message(target_chat_id, message, silent=u.get("silent", False))

            except Exception as e:
                print(f"❗ خطا در بررسی {u.get('alias', '?')}: {e}")

        await asyncio.sleep(check_interval)


@client.on(events.NewMessage())
async def command_handler(event):
    sender = await event.get_sender()
    if sender.username != ADMIN_USERNAME:
        return

    text = event.raw_text.strip()

    if text.lower() == "start":
        if running_event.is_set():
            await event.reply("⚠️ ربات قبلاً فعال است.")
        else:
            running_event.set()
            await event.reply("🚀 ربات شروع به کار کرد.")

    elif text.lower() == "stop":
        if not running_event.is_set():
            await event.reply("⚠️ ربات قبلاً متوقف شده است.")
        else:
            running_event.clear()
            await event.reply("🛑 ربات متوقف شد.")

    elif text.lower() == "log":
        if os.path.exists("status_log.json"):
            await client.send_file(event.chat_id, "status_log.json", caption="📂 فایل لاگ وضعیت‌ها")
        else:
            await event.reply("⚠️ فایل لاگ پیدا نشد.")

    elif text.lower() == "clearlog":
        if os.path.exists("status_log.json"):
            with open("status_log.json", "w", encoding="utf-8") as f:
                f.write("[]")
            log.clear()
            await event.reply("🗑️ فایل لاگ پاک شد.")
        else:
            await event.reply("⚠️ فایل لاگ وجود ندارد.")

    elif text.lower() == "status":
        status_text = "🚀 ربات فعال است." if running_event.is_set() else "⏸️ ربات متوقف شده است."
        status_text += f"\n⏲️ بازه بررسی وضعیت: {check_interval} ثانیه"
        await event.reply(status_text)

    elif text.lower() == "users":
        if users_to_monitor:
            message_lines = ["👥 لیست کاربران تحت نظر:"]
            for i, user in enumerate(users_to_monitor, 1):
                alias = user.get("alias", "بی‌نام")
                username_or_id = user.get("username", "نامشخص")

                display_name = ""
                try:
                    if isinstance(username_or_id, int):
                        entity = await client.get_entity(username_or_id)
                        uname = entity.username if entity.username else str(username_or_id)
                        display_name = f"@{uname}" if entity.username else uname
                    else:
                        display_name = f"@{username_or_id}"
                except:
                    display_name = str(username_or_id)

                message_lines.append(f"🔸 {i}. {alias} ({display_name})")

            message = "\n".join(message_lines)
            await event.reply(message)
        else:
            await event.reply("⚠️ لیست کاربران خالی است.")

    elif text.lower().startswith("deluser"):
        parts = text.split()
        if len(parts) != 2:
            await event.reply("❌ فرمت دستور اشتباه است.\n\nفرمت صحیح:\ndeluser شماره_کاربر")
            return

        try:
            index = int(parts[1]) - 1
        except ValueError:
            await event.reply("❌ شماره کاربر باید عدد باشد.")
            return

        if index < 0 or index >= len(users_to_monitor):
            await event.reply("⚠️ شماره کاربر نامعتبر است.")
            return

        removed_user = users_to_monitor.pop(index)

        users_to_save = []
        for u in users_to_monitor:
            user_copy = u.copy()
            if "entity" in user_copy:
                del user_copy["entity"]
            users_to_save.append(user_copy)

        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users_to_save, f, indent=2, ensure_ascii=False)

        await event.reply(f"✅ کاربر `{removed_user.get('alias', 'بی‌نام')}` با شماره {index+1} حذف شد.")

    elif text.lower().startswith("report"):
        report = parse_status_log_file()
        await event.respond(report)
            
    elif text.lower().startswith("adduser"):
        parts = text.split()
        if len(parts) < 3:
            await event.reply("❌ فرمت دستور اشتباه است.\n\nفرمت صحیح:\nadduser alias username_or_id")
            return

        username_or_id = parts[-1]
        alias = " ".join(parts[1:-1])

        if username_or_id.startswith("@"):
            username_or_id = username_or_id[1:]

        user_id = None
        try:
            user_id = int(username_or_id)
        except ValueError:
            try:
                entity = await client.get_entity(username_or_id)
                user_id = entity.id
            except Exception as e:
                await event.reply(f"❌ یوزرنیم `{username_or_id}` معتبر نیست یا پیدا نشد.\nخطا: {e}")
                return

        if any(u["username"] == user_id for u in users_to_monitor):
            await event.reply(f"⚠️ کاربر با شناسه `{user_id}` قبلاً در لیست وجود دارد.")
            return

        new_user = {
            "alias": alias,
            "username": user_id,
            "silent": False
        }
        users_to_monitor.append(new_user)

        users_to_save = []
        for u in users_to_monitor:
            user_copy = u.copy()
            if "entity" in user_copy:
                del user_copy["entity"]
            users_to_save.append(user_copy)

        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users_to_save, f, indent=2, ensure_ascii=False)

        try:
            entity = await client.get_entity(user_id)
            new_user["entity"] = entity
            user_status_map[entity.id] = None
        except Exception as e:
            print(f"❗ خطا در بارگذاری entity جدید: {e}")

        await event.reply(f"✅ کاربر جدید با نام مستعار `{alias}` و شناسه `{user_id}` اضافه شد.")

    elif text.lower().startswith("info"):
        parts = text.split()
        if len(parts) != 2:
            await event.reply("❌ فرمت دستور اشتباه است.\n\nفرمت صحیح:\ninfo شماره_کاربر")
            return

        try:
            index = int(parts[1]) - 1
        except ValueError:
            await event.reply("❌ شماره کاربر باید عدد باشد.")
            return

        if index < 0 or index >= len(users_to_monitor):
            await event.reply("⚠️ شماره کاربر نامعتبر است.")
            return

        user = users_to_monitor[index]

        alias = user.get("alias", "بی‌نام")
        username_or_id = user.get("username", "نامشخص")
        silent_mode = user.get("silent", False)

        try:
            entity = await client.get_entity(username_or_id)
            uname = entity.username if entity.username else str(username_or_id)
            display_name = f"@{uname}" if entity.username else uname

            user_obj = await client.get_entity(entity.id)
            status = user_obj.status
            status_name = status.__class__.__name__ if status else "UserStatusEmpty"
            translated_status = status_translations.get(status_name, status_name)
        except Exception as e:
            display_name = str(username_or_id)
            translated_status = "⛔ اطلاعات وضعیت قابل دریافت نیست"

        info_message = (
            f"👤 اطلاعات کاربر شماره {index+1}:\n"
            f"نام مستعار: {alias}\n"
            f"شناسه/یوزرنیم: {display_name}\n"
            f"حالت سکوت: {'✅ فعال' if silent_mode else '❌ غیرفعال'}\n"
            f"وضعیت فعلی: {translated_status}"
        )

        await event.reply(info_message)

    elif text.lower() == "help":
        help_text = (
            "📚 دستورهای ربات:\n\n"
            "start - شروع به کار ربات\n"
            "stop - توقف ربات\n"
            "status - نمایش وضعیت فعلی ربات\n"
            # "setinterval ثانیه - تنظیم بازه زمانی بررسی وضعیت\n"
            "log - دریافت فایل لاگ وضعیت‌ها\n"
            "clearlog - پاک کردن فایل لاگ\n"
            "users - نمایش لیست کاربران تحت نظر\n"
            "adduser alias username_or_id - اضافه کردن کاربر جدید\n"
            "deluser شماره_کاربر - حذف کاربر با شماره\n"
            "info شماره_کاربر - نمایش اطلاعات دقیق یک کاربر\n"
            "help - نمایش این راهنما\n"
        )
        await event.reply(help_text)
        
    else:
        await event.reply("❓ دستور شناخته نشده است.")

async def main():
    while True:
        try:
            await client.start()
            await client.send_message(ADMIN_USERNAME , "🤖 ربات با موفقیت راه‌اندازی شد و آماده اجراست.")
            asyncio.create_task(detect_lastsin_multi())
            print("🤖 ربات اجرا شد و در حال گوش دادن به دستورات...")
            await client.run_until_disconnected()
        except Exception as e:
            print(f"❗ خطا در اجرای اصلی: {e}")
            try:
                await client.send_message(ADMIN_USERNAME, f"❌ خطا در اجرای ربات:\n{e}\n⏳ تلاش برای اجرای مجدد پس از ۱ ساعت...")
            except:
                print("⚠️ ارسال پیام به ادمین ناموفق بود.")
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())