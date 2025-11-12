import streamlit as st
import pandas as pd
import datetime
import os
import random
import matplotlib.pyplot as plt

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="NuTraDaily", page_icon="logo.png", layout="wide")

# -------------------------------
# CSS
# -------------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: url('background.jpg') no-repeat center center fixed;
    background-size: cover;
    color: #1b4332;
    font-family: 'Poppins', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1b4332 0%, #2d6a4f 100%);
    color: white;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, 
[data-testid="stSidebar"] label, [data-testid="stSidebar"] div {
    color: white !important;
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

/* Logo and Title */
.logo {
    display: block;
    margin: auto;
    width: 130px;
    animation: spin 4s linear infinite;
}
@keyframes spin {
    from {transform: rotate(0deg);}
    to {transform: rotate(360deg);}
}
.title {
    text-align: center;
    font-size: 36px;
    font-weight: 700;
    margin-top: -10px;
    color: #1b4332;
}

/* Login/Signup */
.login-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 70vh;
    gap: 20px;
}
.action-button {
    width: 220px;
    font-size: 18px;
    padding: 12px 0;
    border-radius: 12px;
    transition: all 0.4s ease;
}
.action-button:hover {
    transform: scale(1.05);
}

/* Animated Form */
.form-container {
    animation: fadeSlide 0.8s ease forwards;
    opacity: 0;
}
@keyframes fadeSlide {
    0% { opacity: 0; transform: translateY(-20px); }
    100% { opacity: 1; transform: translateY(0); }
}

/* Dashboard Header */
.dashboard-header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15px;
    margin-bottom: 10px;
}
.dashboard-header img {
    width: 60px;
    animation: spin 5s linear infinite;
}
.dashboard-header h1 {
    color: #1b4332;
    font-size: 32px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# FILE SETUP
# -------------------------------
user_file = "users.csv"
cols = ["Name", "Email", "Password", "Height", "Weight", "Gender", "Activity", "Goal"]
if not os.path.exists(user_file):
    pd.DataFrame(columns=cols).to_csv(user_file, index=False)

# -------------------------------
# FUNCTIONS
# -------------------------------
def load_users():
    return pd.read_csv(user_file)

def save_user(data):
    df = load_users()
    if data["Email"] in df["Email"].values:
        st.warning("⚠️ Email already registered! Please log in.")
        return False
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(user_file, index=False)
    st.success("✅ Sign-up successful! Please log in.")
    return True

def authenticate(email, password):
    df = load_users()
    user = df[(df["Email"] == email) & (df["Password"] == password)]
    return not user.empty

# -------------------------------
# LANDING (Animated)
# -------------------------------
def landing_page():
    st.markdown('<img src="logo.png" class="logo">', unsafe_allow_html=True)
    st.markdown('<h1 class="title">NuTraDaily</h1>', unsafe_allow_html=True)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    if st.button("🔐 Login", key="login_main", help="Tap to login", use_container_width=False):
        st.session_state.page = "login"
    if st.button("📝 Sign Up", key="signup_main", help="Tap to sign up", use_container_width=False):
        st.session_state.page = "signup"
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# SIGN UP FORM
# -------------------------------
def signup_page():
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<img src="logo.png" class="logo">', unsafe_allow_html=True)
    st.markdown('<h1 class="title">NuTraDaily</h1>', unsafe_allow_html=True)
    st.subheader("📝 Create Account")

    with st.form("signup_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        height = st.number_input("Height (cm)", 50.0, 250.0)
        weight = st.number_input("Weight (kg)", 10.0, 300.0)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"])
        goal = st.selectbox("Goal", ["Weight Loss", "Weight Gain", "Maintenance"])
        submitted = st.form_submit_button("Sign Up ✅")
        if submitted:
            save_user({
                "Name": name, "Email": email, "Password": password,
                "Height": height, "Weight": weight,
                "Gender": gender, "Activity": activity, "Goal": goal
            })
    if st.button("⬅ Back"):
        st.session_state.page = "landing"
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# LOGIN FORM
# -------------------------------
def login_page():
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<img src="logo.png" class="logo">', unsafe_allow_html=True)
    st.markdown('<h1 class="title">NuTraDaily</h1>', unsafe_allow_html=True)
    st.subheader("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login ✅"):
        if authenticate(email, password):
            st.session_state.logged_in = True
            st.session_state.user_email = email
        else:
            st.error("❌ Invalid credentials.")
    if st.button("⬅ Back"):
        st.session_state.page = "landing"
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# FEATURE PAGES
# -------------------------------
def about_us():
    st.title("🌿 About Us")
    st.write("""
    Welcome to **NuTraDaily** — your personal health companion 🌱  
    We help you track nutrition, hydration, and progress in a smart, visual, and effortless way.  
    Stay healthy, stay strong 💪  
    """)

def water_tracker():
    st.title("💧 Water Tracker")
    goal = st.number_input("Enter daily goal (liters):", 0.5, 10.0, 2.0)
    consumed = st.number_input("Water consumed (liters):", 0.0, goal, 1.0)
    progress = (consumed / goal) * 100 if goal > 0 else 0
    st.progress(progress / 100)
    st.info(f"💦 You’ve reached {progress:.1f}% of your daily goal!")

def nutrition():
    st.title("🍎 Nutrition Tracker")
    calories = st.number_input("Calories consumed today:", 0)
    goal = st.number_input("Target daily calories:", 1000)
    st.progress(min(calories / goal, 1.0))
    st.info(f"🔥 {calories} / {goal} kcal")

def progress_page():
    st.title("🎯 Progress Tracker")
    dates = pd.date_range(datetime.datetime.now() - datetime.timedelta(days=6), datetime.datetime.now())
    progress = [random.randint(50, 100) for _ in range(7)]
    plt.plot(dates, progress, marker='o')
    plt.title("Weekly Goal Progress")
    st.pyplot(plt)

def streaks():
    st.title("🔥 Streaks")
    streak = random.randint(1, 20)
    st.success(f"🔥 You’ve maintained your streak for {streak} days straight!")

# -------------------------------
# DASHBOARD
# -------------------------------
def dashboard():
    st.markdown("""
    <div class="dashboard-header">
        <img src="logo.png">
        <h1>NuTraDaily</h1>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.title("📋 Dashboard")
    choice = st.sidebar.radio("Navigate", ["🌿 About Us", "🍎 Nutrition", "💧 Water Tracker", "🎯 Progress", "🔥 Streaks"])

    if choice == "🌿 About Us":
        about_us()
    elif choice == "🍎 Nutrition":
        nutrition()
    elif choice == "💧 Water Tracker":
        water_tracker()
    elif choice == "🎯 Progress":
        progress_page()
    elif choice == "🔥 Streaks":
        streaks()

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "landing"

# -------------------------------
# MAIN FLOW
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "landing"

if st.session_state.logged_in:
    dashboard()
else:
    if st.session_state.page == "landing":
        landing_page()
    elif st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "signup":
        signup_page()
