import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go

status_translations = {
    "UserStatusOnline": "✅ آنلاین",
    "UserStatusOffline": "🔻 آفلاین",
    "UserStatusRecently": "🕒 اخیراً آنلاین",
    "UserStatusLastWeek": "📅 هفته گذشته",
    "UserStatusLastMonth": "📆 ماه گذشته",
    "UserStatusEmpty": "⛔ بدون اطلاعات"
}

with open("status_log.json", "r", encoding="utf-8") as f:
    data = json.load(f)

if not data:
    st.title("📊 Telegram Last Seen Monitor")
    st.warning("👓 هیچ دیتایی برای نمایش وجود ندارد. منتظر ثبت لاگ ها باشید")
    st.stop()

df = pd.DataFrame(data)
df["time"] = pd.to_datetime(df["time"])
df["translated_status"] = df["status"].map(status_translations)

st.title("📊 Telegram Last Seen Monitor")
st.markdown("نمودارها و آمار وضعیت کاربران رصد شده")

user_alias = st.selectbox("👤 انتخاب کاربر", sorted(df["alias"].unique()))
user_df = df[df["alias"] == user_alias].sort_values("time", ascending=False)

st.subheader("🕒 آخرین وضعیت")
st.write(user_df.iloc[0][["translated_status", "time"]])

st.subheader("📈 نمودار تغییر وضعیت‌ها")

status_map = {
    "✅ برخط": 2,
    "🕒 اخیراً برخط": 1,
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

st.subheader("📋 جدول کامل وضعیت‌ها")
st.dataframe(user_df[["time", "translated_status"]].rename(columns={"translated_status": "وضعیت"}))
user_df_filtered = user_df[["time", "translated_status"]].rename(columns={"translated_status": "وضعیت"})
txt_data = user_df_filtered.to_string(index=False)

col1, col2 = st.columns(2)

with col1:
    st.download_button(
        label="گزارش TXT دانلود فایل 💾",
        data=txt_data,
        file_name=f"{user_alias}_status_log.txt",
        mime="text/plain",
    )

with col2:
    if st.button(type="primary" , label=" پاک کردن کل لاگ‌ها 🗑️"):
        with open("status_log.json", "w", encoding="utf-8") as f:
            f.write("[]")
        st.success("تمام لاگ‌ها پاک شدند. لطفاً صفحه را دوباره بارگذاری کنید.")

st.subheader("📊 آمار وضعیت‌ها")
st.write(user_df["translated_status"].value_counts())
