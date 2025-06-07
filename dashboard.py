import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from collections import Counter



# مترجم وضعیت‌ها
status_translations = {
    "UserStatusOnline": "✅ آنلاین",
    "UserStatusOffline": "🔻 آفلاین",
    "UserStatusRecently": "🕒 اخیراً آنلاین",
    "UserStatusLastWeek": "📅 هفته گذشته",
    "UserStatusLastMonth": "📆 ماه گذشته",
    "UserStatusEmpty": "⛔ بدون اطلاعات"
}

# Load log
with open("status_log.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)
df["time"] = pd.to_datetime(df["time"])
df["translated_status"] = df["status"].map(status_translations)

st.title("📊 Telegram Last Seen Monitor")
st.markdown("نمودارها و آمار وضعیت کاربران رصد شده")

# انتخاب کاربر
user_alias = st.selectbox("👤 انتخاب کاربر", sorted(df["alias"].unique()))
user_df = df[df["alias"] == user_alias].sort_values("time", ascending=False)

# آخرین وضعیت
st.subheader("🕒 آخرین وضعیت")
st.write(user_df.iloc[0][["translated_status", "time"]])

# نمودار وضعیت
st.subheader("📈 نمودار تغییر وضعیت‌ها")

status_map = {
    "✅ آنلاین": 2,
    "🕒 اخیراً آنلاین": 1,
    "🔻 آفلاین": 0
}

user_df["status_num"] = user_df["translated_status"].map(status_map)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=user_df["time"],
    y=user_df["status_num"],
    mode='lines+markers',
    line_shape='hv',
    marker=dict(size=6),
    line=dict(width=2)
))

fig.update_layout(
    font=dict(family="Vazir, sans-serif"),
    title="📈 تغییرات وضعیت کاربر",
    xaxis_title="🕒 زمان",
    yaxis=dict(
        title="📶 وضعیت",
        tickmode="array",
        tickvals=[0, 1, 2],
        ticktext=["🔻 آفلاین", "🕒 اخیراً", "✅ آنلاین"]
    ),
    height=500
)

st.plotly_chart(fig)

# آمار وضعیت‌ها
st.subheader("📊 آمار وضعیت‌ها")
st.write(user_df["translated_status"].value_counts())

# جدول کامل
st.subheader("📋 جدول کامل وضعیت‌ها")
st.dataframe(user_df[["time", "translated_status"]].rename(columns={"translated_status": "وضعیت"}))


st.write("💡 فونت:", st.get_option("theme.font"))
