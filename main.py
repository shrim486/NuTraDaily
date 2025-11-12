import streamlit as st
import pandas as pd
import datetime
import os
import random
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# ------------------------------------------------
# PAGE CONFIG (App icon = logo)
# ------------------------------------------------
st.set_page_config(page_title="NuTraDaily", page_icon="logo.png", layout="wide")

# ------------------------------------------------
# IMAGE HANDLING (Ensures logo, title & bg work everywhere)
# ------------------------------------------------
def load_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

bg_base64 = load_image_base64("background.jpg")
logo_base64 = load_image_base64("logo.png")
title_base64 = load_image_base64("title.png")

# ------------------------------------------------
# CUSTOM CSS (Optimized for speed)
# ------------------------------------------------
css = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: url("data:image/jpg;base64,{bg_base64 if bg_base64 else ''}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    font-family: 'Poppins', sans-serif;
    color: #1b4332;
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #1b4332 0%, #2d6a4f 100%);
    color: #ffffff;
}}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] label, 
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] div {{
    color: #f1faee !important;
    font-weight: 600 !important;
}}

button {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    background-color: #52b788 !important;
    color: white !important;
}}
button:hover {{
    background-color: #40916c !important;
}}

.logo {{
    position: absolute;
    top: 15px;
    left: 25px;
    width: 80px;
}}
.title-image {{
    display: block;
    margin: auto;
    width: 280px;
}}

.addon-space {{
    display: flex;
    justify-content: center;
    gap: 25px;
    margin-top: 40px;
}}
.addon-space img {{
    width: 120px;
    border-radius: 10px;
    cursor: pointer;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ------------------------------------------------
# USER FILE HANDLING (error-proof)
# ------------------------------------------------
user_file = "users.csv"
expected_cols = ["Name", "Email", "Password", "Height", "Weight", "Gender", "Activity", "Goal"]

if not os.path.exists(user_file):
    pd.DataFrame(columns=expected_cols).to_csv(user_file, index=False)
else:
    try:
        df = pd.read_csv(user_file)
        if list(df.columns) != expected_cols:
            pd.DataFrame(columns=expected_cols).to_csv(user_file, index=False)
    except Exception:
        pd.DataFrame(columns=expected_cols).to_csv(user_file, index=False)

def load_users():
    return pd.read_csv(user_file)

def save_user(data):
    df = load_users()
    if data["Email"] in df["Email"].values:
        st.warning("⚠️ Email already registered! Please log in instead.")
        return False
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(user_file, index=False)
    st.success("✅ Sign-up successful! You can now log in.")
    return True

def authenticate(email, password):
    df = load_users()
    user = df[(df["Email"] == email) & (df["Password"] == password)]
    return not user.empty

# ------------------------------------------------
# AUTH PAGES
# ------------------------------------------------
def signup_page():
    if logo_base64:
        st.markdown(f'<img src="data:image/png;base64,{logo_base64}" class="logo">', unsafe_allow_html=True)
    if title_base64:
        st.markdown(f'<img src="data:image/png;base64,{title_base64}" class="title-image">', unsafe_allow_html=True)

    st.subheader("📝 Sign Up for NuTraDaily")
    with st.form("signup_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0)
        weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        activity = st.selectbox("Physical Activity Level", ["Low", "Moderate", "High"])
        goal = st.selectbox("Goal", ["Weight Loss", "Weight Gain", "Maintenance"])
        submit = st.form_submit_button("Sign Up ✅")

        if submit:
            save_user({
                "Name": name, "Email": email, "Password": password,
                "Height": height, "Weight": weight, "Gender": gender,
                "Activity": activity, "Goal": goal
            })

    st.markdown("---")
    st.info("Already have an account?")
    if st.button("🔑 Go to Login"):
        st.session_state.page = "login"

def login_page():
    if logo_base64:
        st.markdown(f'<img src="data:image/png;base64,{logo_base64}" class="logo">', unsafe_allow_html=True)
    if title_base64:
        st.markdown(f'<img src="data:image/png;base64,{title_base64}" class="title-image">', unsafe_allow_html=True)

    st.subheader("🔐 Login to NuTraDaily")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login ✅"):
        if authenticate(email, password):
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success("🎉 Login successful!")
        else:
            st.error("❌ Invalid email or password!")

    st.markdown("---")
    st.info("Don't have an account?")
    if st.button("📝 Go to Sign Up"):
        st.session_state.page = "signup"

# ------------------------------------------------
# APP FEATURES
# ------------------------------------------------
def water_tracker():
    st.title("💧 Water Tracker")
    goal = st.number_input("Daily water goal (liters):", 0.5, 10.0, step=0.5)
    consumed = st.number_input("Consumed so far (liters):", 0.0, goal, step=0.1)
    percent = (consumed / goal) * 100 if goal else 0
    st.progress(percent / 100)
    st.info(f"💦 {percent:.1f}% of goal reached")

def nutrition_page():
    st.title("🍎 Nutrition & Diet Plan")
    cal = st.number_input("Calories consumed today:", min_value=0)
    target = st.number_input("Target calories:", min_value=1000)
    st.progress(min(cal / target, 1.0))
    st.info(f"🔥 {cal} / {target} kcal")

def goal_progress():
    st.title("🎯 Goal Progress")
    dates = pd.date_range(datetime.datetime.now() - datetime.timedelta(days=6), datetime.datetime.now())
    progress = [random.randint(50, 100) for _ in range(7)]
    plt.plot(dates, progress, marker='o')
    plt.ylabel("Goal Achievement (%)")
    st.pyplot(plt)

def daily_streak():
    st.title("🔥 Daily Streaks & Achievements")
    streak_days = random.randint(1, 15)
    st.success(f"🔥 You've maintained your streak for {streak_days} days straight!")

# ------------------------------------------------
# MAIN APP
# ------------------------------------------------
def main_app():
    if logo_base64:
        st.markdown(f'<img src="data:image/png;base64,{logo_base64}" class="logo">', unsafe_allow_html=True)
    if title_base64:
        st.markdown(f'<img src="data:image/png;base64,{title_base64}" class="title-image">', unsafe_allow_html=True)

    greeting = "🌞 Good morning!" if datetime.datetime.now().hour < 12 else \
               "🌤️ Good afternoon!" if datetime.datetime.now().hour < 17 else "🌙 Good evening!"
    st.toast(f"{greeting} Stay consistent 💪", icon="💪")

    st.sidebar.title("📋 Dashboard")
    choice = st.sidebar.radio("Navigate", ["🏠 Home", "🍎 Nutrition", "💧 Water Tracker", "🎯 Progress", "🔥 Streaks"])

    if choice == "🏠 Home":
        st.title("🌿 Welcome to NuTraDaily!")
        st.write("Your all-in-one wellness tracking dashboard.")
        st.markdown("""
        <div class="addon-space">
            <a href="#"><img src="https://via.placeholder.com/120x120.png?text=Add-On+1"></a>
            <a href="#"><img src="https://via.placeholder.com/120x120.png?text=Add-On+2"></a>
        </div>
        """, unsafe_allow_html=True)
    elif choice == "🍎 Nutrition":
        nutrition_page()
    elif choice == "💧 Water Tracker":
        water_tracker()
    elif choice == "🎯 Progress":
        goal_progress()
    elif choice == "🔥 Streaks":
        daily_streak()

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"

# ------------------------------------------------
# SESSION NAVIGATION
# ------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.logged_in:
    main_app()
else:
    if st.session_state.page == "signup":
        signup_page()
    else:
        login_page()
