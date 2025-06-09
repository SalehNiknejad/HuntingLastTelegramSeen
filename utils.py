from collections import defaultdict
from datetime import datetime, timedelta
import json

ONLINE_STATUSES = {"UserStatusOnline"}
OFFLINE_STATUSES = {"UserStatusOffline", "UserStatusRecently", "UserStatusLastWeek", "UserStatusLastMonth", "UserStatusOfflineApprox"}

def parse_status_log_file(filepath="status_log.json"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return f"❌ خطا در بارگذاری فایل: {e}"

    user_logs = defaultdict(list)
    for entry in data:
        username = entry.get("alias")
        try:
            timestamp = datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S")
        except:
            timestamp = datetime.fromisoformat(entry["time"])
        status = entry.get("status")
        user_logs[username].append((timestamp, status))

    results = {}
    for username, logs in user_logs.items():
        logs.sort()
        total_online = timedelta()
        start_time = None
        for timestamp, status in logs:
            if status in ONLINE_STATUSES:
                start_time = timestamp
            elif status in OFFLINE_STATUSES and start_time:
                total_online += (timestamp - start_time)
                start_time = None

        minutes = int(total_online.total_seconds() // 60)
        seconds = int(total_online.total_seconds() % 60)
        results[username] = (minutes, seconds)

    return format_report(results)

def format_report(results):
    report_lines = []
    sorted_users = sorted(results.items(), key=lambda x: x[1][0]*60 + x[1][1], reverse=True)

    for username, (m, s) in sorted_users:
        line = f"{username} \n {m} دقیقه و {s} ثانیه آنلاین بوده."
        if m == 0 and s == 0:
            line += " ❌"
        report_lines.append(line)

    top_users = [u for u in sorted_users if u[1][0] >= 60]
    if top_users:
        report_lines.insert(0, "\n📈 بیشترین زمان آنلاین بودن:")
        report_lines.insert(1,"")
        for username, (m, s) in top_users[:3]:
            report_lines.insert(1, f"- {username}: {m} دقیقه و {s} ثانیه")

    return "\n".join(report_lines)