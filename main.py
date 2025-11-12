import streamlit as st
import pandas as pd
import datetime
import os
import time
import random
import base64
import matplotlib.pyplot as plt

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(page_title="NuTraDaily", page_icon="logo.png", layout="wide")

# ------------------------------------------------
# BACKGROUND + STYLE
# ------------------------------------------------
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

def add_bg():
    if os.path.exists("background.jpg"):
        bg = get_base64("background.jpg")
        st.markdown(
            f"""
            <style>
            [data-testid="stAppViewContainer"] {{
                background: url("data:image/jpg;base64,{bg}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                font-family: 'Poppins', sans-serif;
                color: #1b4332;
            }}
            [data-testid="stSidebar"] {{
                background: linear-gradient(180deg, #1b4332 0%, #2d6a4f 100%);
                color: white;
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
                display:block;
                margin:auto;
                width:120px;
            }}
            .title {{
                display:block;
                margin:auto;
                width:300px;
            }}
            .icon-choice {{
                display:flex;
                justify-content:center;
                align-items:center;
                gap:80px;
                margin-top:60px;
            }}
            .icon-choice img {{
                width:120px;
                height:auto;
                cursor:pointer;
                transition:transform 0.3s ease;
            }}
            .icon-choice img:hover {{
                transform:scale(1.1);
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

add_bg()

# ------------------------------------------------
# USER DATA HANDLING
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
# LOADING ANIMATION
# ------------------------------------------------
def loading_animation():
    with st.spinner("Loading your NuTraDaily experience... 🚴‍♂️"):
        time.sleep(2)
    st.success("✨ Ready!")

# ------------------------------------------------
# PAGES
# ------------------------------------------------
def show_logo_title():
    if os.path.exists("logo.png"):
        st.markdown('<img src="logo.png" class="logo">', unsafe_allow_html=True)
    if os.path.exists("title.png"):
        st.markdown('<img src="title.png" class="title">', unsafe_allow_html=True)

def intro_screen():
    show_logo_title()
    st.markdown("<h3 style='text-align:center;margin-top:30px;'>Welcome to NuTraDaily</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Choose your path to get started</p>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='icon-choice'>
            <img src='https://cdn-icons-png.flaticon.com/512/747/747376.png' alt='Login' onclick='window.location.href="?page=login"'/>
            <img src='https://cdn-icons-png.flaticon.com/512/2921/2921222.png' alt='Signup' onclick='window.location.href="?page=signup"'/>
        </div>
        """,
        unsafe_allow_html=True,
    )

def signup_page():
    show_logo_title()
    st.subheader("📝 Create your NuTraDaily Account")

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
            if save_user({
                "Name": name,
                "Email": email,
                "Password": password,
                "Height": height,
                "Weight": weight,
                "Gender": gender,
                "Activity": activity,
                "Goal": goal
            }):
                st.session_state.page = "login"

def login_page():
    show_logo_title()
    st.subheader("🔐 Log In to NuTraDaily")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login ✅"):
        if authenticate(email, password):
            st.session_state.logged_in = True
            st.session_state.user_email = email
            loading_animation()
            st.success("🎉 Login successful!")
        else:
            st.error("❌ Invalid email or password!")

def water_tracker():
    st.title("💧 Water Tracker")
    goal = st.number_input("Daily goal (liters):", min_value=0.5, max_value=10.0, step=0.5)
    consumed = st.number_input("Consumed (liters):", min_value=0.0, max_value=goal, step=0.1)
    progress = (consumed / goal) * 100 if goal > 0 else 0
    st.progress(progress / 100)
    st.info(f"💦 You’ve reached {progress:.1f}% of your daily goal!")

def nutrition_page():
    st.title("🍎 Nutrition & Diet Plan")
    calories = st.number_input("Calories consumed today:", min_value=0)
    target = st.number_input("Target daily calories:", min_value=1000)
    st.progress(min(calories / target, 1.0))
    st.info(f"🔥 {calories} / {target} kcal")

def goal_progress():
    st.title("🎯 Goal Progress")
    dates = pd.date_range(datetime.datetime.now() - datetime.timedelta(days=6), datetime.datetime.now())
    progress = [random.randint(50, 100) for _ in range(7)]
    plt.plot(dates, progress, marker='o')
    plt.title("Weekly Progress")
    plt.ylabel("Goal Achievement (%)")
    st.pyplot(plt)

def streaks():
    st.title("🔥 Daily Streaks & Achievements")
    days = random.randint(1, 15)
    st.success(f"🔥 You’ve maintained your streak for {days} days straight!")

def main_app():
    show_logo_title()

    current_hour = datetime.datetime.now().hour
    greeting = "🌞 Good morning!" if current_hour < 12 else "🌤️ Good afternoon!" if current_hour < 17 else "🌙 Good evening!"
    st.toast(f"{greeting} Keep moving forward!", icon="💪")

    st.sidebar.title("📋 Dashboard")
    choice = st.sidebar.radio("Navigate", ["🏠 Home", "🍎 Nutrition", "💧 Water Tracker", "🎯 Progress", "🔥 Streaks"])

    if choice == "🏠 Home":
        st.title("🌿 Welcome to NuTraDaily!")
        st.write("Your all-in-one health tracking dashboard.")
        st.markdown(
            """
            <div style="display:flex;justify-content:center;gap:25px;margin-top:30px;">
                <a href="#"><img src="https://via.placeholder.com/120x120.png?text=Add-On+1"></a>
                <a href="#"><img src="https://via.placeholder.com/120x120.png?text=Add-On+2"></a>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif choice == "🍎 Nutrition":
        nutrition_page()
    elif choice == "💧 Water Tracker":
        water_tracker()
    elif choice == "🎯 Progress":
        goal_progress()
    elif choice == "🔥 Streaks":
        streaks()

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "intro"

# ------------------------------------------------
# STATE MANAGEMENT
# ------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "intro"

# ------------------------------------------------
# NAVIGATION
# ------------------------------------------------
if st.session_state.logged_in:
    main_app()
else:
    if st.session_state.page == "signup":
        signup_page()
    elif st.session_state.page == "login":
        login_page()
    else:
        intro_screen()
