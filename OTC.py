import streamlit as st
import json
from datetime import datetime, timedelta
from collections import defaultdict

st.markdown(
    """
    <style>


    html, body, div, span, input, textarea, button, label, .stTextArea, .stButton, .stTextInput, .stSelectbox, .stText , .subheader {
      text-align: right !important;
      direction: rtl !important;
    }

    .stTextArea textarea, .stButton button , .subheader , .stTextInput input, .stSelectbox select {
        text-align: right !important;
    }

    .stText, .stSubheader, .stTitle {
        text-align: right !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

ONLINE_STATUSES = {"UserStatusOnline", "✅ آنلاین", "Online"}
OFFLINE_STATUSES = {"UserStatusOffline", "🔻 آفلاین", "Offline"}

def parse_status_log(uploaded_file):
    try:
        data = json.load(uploaded_file)
    except Exception as e:
        return f"❌ خطا در بارگذاری فایل: {e}"

    user_logs = defaultdict(list)
    for entry in data:
        username = entry.get("alias")
        timestamp = datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S")
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

# Streamlit UI
st.title("📊 گزارش دقیق زمان آنلاین کاربران")
st.markdown("""
برای شروع، فایل `status_log.json` را انتخاب کن. گزارش به صورت خودکار تولید می‌شود.
""")

uploaded_file = st.file_uploader("انتخاب فایل JSON", type="json")

if uploaded_file:
    with st.spinner("در حال پردازش..."):
        result = parse_status_log(uploaded_file)
    st.success("✅ گزارش آماده است:")
    st.text_area("📋 گزارش کلی کاربران:", result, height=500)
else:
    st.info("لطفاً یک فایل JSON انتخاب کن.")