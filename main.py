import streamlit as st
import pandas as pd
import datetime
import os
import random

# -------------------------------
# PAGE CONFIG (using logo as icon)
# -------------------------------
st.set_page_config(
    page_title="NuTraDaily",
    page_icon="logo.png",
    layout="wide"
)

# -------------------------------
# BACKGROUND IMAGE & GLOBAL STYLE
# -------------------------------
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: url("background.jpg") no-repeat center center fixed;
    background-size: cover;
    font-family: 'Poppins', sans-serif;
    color: #1b4332;
}

/* Sidebar hidden */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0);
}

/* Buttons */
button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    background-color: #52b788 !important;
    color: white !important;
}
button:hover {
    background-color: #40916c !important;
}

/* Center main logo and title */
.header-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15px;
}
.header-container img {
    height: 80px;
}

/* Corner logo */
.corner-logo {
    position: absolute;
    top: 20px;
    left: 20px;
}
.corner-logo img {
    width: 90px;
    border-radius: 10px;
}

/* Login/Signup Buttons bottom corner */
.login-buttons {
    position: fixed;
    bottom: 25px;
    right: 25px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.login-buttons button {
    width: 140px;
    font-size: 15px;
}

/* Add-on space */
.addon-space {
    margin-top: 60px;
    text-align: center;
}
.addon-space img {
    width: 200px;
    margin: 10px;
    border-radius: 15px;
    transition: transform 0.2s;
}
.addon-space img:hover {
    transform: scale(1.05);
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -------------------------------
# FILE SETUP
# -------------------------------
user_file = "users.csv"
if not os.path.exists(user_file):
    pd.DataFrame(columns=["Name", "Email", "Password", "Height", "Weight", "Gender", "Activity", "Goal"]).to_csv(user_file, index=False)

# -------------------------------
# SESSION STATE
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = ""

# -------------------------------
# FUNCTIONS
# -------------------------------
def save_user(data):
    df = pd.read_csv(user_file)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(user_file, index=False)

def verify_user(email, password):
    df = pd.read_csv(user_file)
    user = df[(df["Email"] == email) & (df["Password"] == password)]
    return not user.empty

# -------------------------------
# LOGIN & SIGNUP FORMS
# -------------------------------
def show_signup():
    st.title("🧾 Create Your NuTraDaily Account")
    with st.form("signup_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        height = st.number_input("Height (cm)", 100, 250, 170)
        weight = st.number_input("Weight (kg)", 30, 200, 65)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"])
        goal = st.radio("Goal", ["Weight Loss", "Weight Gain", "Maintain"])
        submitted = st.form_submit_button("Sign Up")

        if submitted:
            if name and email and password:
                save_user({
                    "Name": name,
                    "Email": email,
                    "Password": password,
                    "Height": height,
                    "Weight": weight,
                    "Gender": gender,
                    "Activity": activity,
                    "Goal": goal
                })
                st.success("✅ Account created successfully! You can now log in.")
            else:
                st.warning("⚠️ Please fill all required fields.")

def show_login():
    st.title("🔐 Login to NuTraDaily")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        if login_btn:
            if verify_user(email, password):
                st.session_state.logged_in = True
                st.session_state.email = email
                st.success("✅ Login successful! Welcome back 🌿")
            else:
                st.error("❌ Invalid credentials.")

# -------------------------------
# MAIN DASHBOARD (AFTER LOGIN)
# -------------------------------
def show_dashboard():
    st.markdown('<div class="corner-logo"><img src="logo.png" alt="logo"></div>', unsafe_allow_html=True)
    st.markdown('<div class="header-container"><img src="title.png" alt="title"></div>', unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center; margin-top:40px;'>Welcome to NuTraDaily 🌱</h2>", unsafe_allow_html=True)

    st.info("💡 Explore your health dashboard, track nutrition, and achieve your goals!")

    # Add-ons space
    st.markdown('<div class="addon-space">', unsafe_allow_html=True)
    st.markdown("<h3>🚀 Coming Soon: Add-ons</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/869/869636.png", caption="AI Food Scanner", use_column_width=False)
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/1256/1256650.png", caption="Workout Tracker", use_column_width=False)
    with col3:
        st.image("https://cdn-icons-png.flaticon.com/512/679/679922.png", caption="Sleep Monitor", use_column_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# RENDER LOGIC
# -------------------------------
if not st.session_state.logged_in:
    # Bottom corner login/signup buttons
    st.markdown("""
        <div class="login-buttons">
            <form action="?page=signup" method="get">
                <button type="submit">Sign Up</button>
            </form>
            <form action="?page=login" method="get">
                <button type="submit">Login</button>
            </form>
        </div>
    """, unsafe_allow_html=True)

    page = st.query_params.get("page", ["home"])[0]

    if page == "signup":
        show_signup()
    elif page == "login":
        show_login()
    else:
        st.markdown('<div class="header-container"><img src="title.png" alt="title"></div>', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; margin-top:60px;'>Welcome to NuTraDaily 🌿</h2>", unsafe_allow_html=True)
        st.info("Track your health, food, and fitness — all in one place!")
else:
    show_dashboard()
