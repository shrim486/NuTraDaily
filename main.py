import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
import random

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="NuTraDaily", page_icon="🥬", layout="wide")

# -------------------------------
# 🌈 CUSTOM CSS — gradient background + branding
# -------------------------------
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: url('https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=1500&q=100');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    font-family: 'Poppins', sans-serif;
    color: #1b4332;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1b4332 0%, #2d6a4f 100%);
    color: #ffffff;
}
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] label, 
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] div {
    color: #f1faee !important;
    font-weight: 600 !important;
}

/* Buttons */
button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    background-color: #52b788 !important;
    color: white !important;
}
button:hover {
    background-color: #40916c !important;
}

/* Card effects */
.stImage, [data-testid="stDataFrame"], .stPlotlyChart {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 15px;
    padding: 10px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

/* Hide default title text in sidebar to use logo */
.sidebar-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 15px 0;
}
.sidebar-logo img {
    width: 180px;
    border-radius: 10px;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -------------------------------
# HEADER WITH PNG LOGO
# -------------------------------
st.image("logo.png", width=250)  # Replace 'logo.png' with your actual logo file

# -------------------------------
# GREETING + MOTIVATION
# -------------------------------
current_hour = datetime.datetime.now().hour

if 0 <= current_hour < 12:
    greeting = "🌞 Good morning!"
elif 12 <= current_hour < 17:
    greeting = "🌤️ Good afternoon!"
else:
    greeting = "🌙 Good evening!"

motivations = [
    "💧 Stay hydrated — your body thanks you for every sip!",
    "🍎 Every healthy choice adds up — keep going!",
    "🏃‍♀️ Don’t stop now! You’re closer than you think!",
    "💚 Your health journey is progress, not perfection.",
    "🌿 Take a deep breath. You’re doing amazing!"
]
st.toast(f"{greeting} {random.choice(motivations)}", icon="💪")

# -------------------------------
# SIDEBAR NAVIGATION (with logo instead of text)
# -------------------------------
st.sidebar.markdown(
    """
    <div class="sidebar-logo">
        <img src="https://your-logo-url-or-local-path/logo.png" alt="NuTraDaily Logo">
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "🍎 Nutrition & Diet", "💧 Water Tracker", "📸 Food Photo", "🎯 Goal Progress", "📊 Weekly Report", "🔥 Daily Streak 🏅"]
)

# -------------------------------
# FILE HANDLING
# -------------------------------
data_file = "progress.csv"
streak_file = "streak.csv"

if not os.path.exists(data_file):
    df = pd.DataFrame(columns=["Date", "Calories", "Water(L)", "GoalWeight"])
    df.to_csv(data_file, index=False)
if not os.path.exists(streak_file):
    s_df = pd.DataFrame(columns=["Date"])
    s_df.to_csv(streak_file, index=False)

# -------------------------------
# PAGES
# -------------------------------
if page == "🏠 Home":
    st.title("Welcome 🌿")
    st.subheader("Your All-in-One Wellness Dashboard")
    st.image("logo.png", width=200)
    st.success("💡 Use the sidebar to explore each section!")

elif page == "🍎 Nutrition & Diet":
    st.title("🍎 Nutrition & Diet Plan")
    # (rest of your existing nutrition code here...)

elif page == "💧 Water Tracker":
    st.title("💧 Water Tracker")
    # (same as before...)

elif page == "📸 Food Photo":
    st.title("📸 Upload Your Meal")
    # (same as before...)

elif page == "🎯 Goal Progress":
    st.title("🎯 Goal Progress")
    # (same as before...)

elif page == "📊 Weekly Report":
    st.title("📊 Weekly Report")
    # (same as before...)

elif page == "🔥 Daily Streak 🏅":
    st.title("🔥 Daily Streak + Achievements 🏅")
    # (same as before...)

# -------------------------------
# FOOTER
# -------------------------------
st.sidebar.markdown("---")
st.sidebar.info("🌿 Made with 💚 — NuTraDaily")
