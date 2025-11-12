import streamlit as st
import pandas as pd
import datetime
import os
import random
import matplotlib.pyplot as plt

# -------------------------------
# PAGE CONFIG (logo as favicon)
# -------------------------------
st.set_page_config(page_title="NuTraDaily", page_icon="logo.png", layout="wide")

# -------------------------------
# 🌈 CUSTOM CSS
# -------------------------------
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: url('background.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    font-family: 'Poppins', sans-serif;
    color: #1b4332;
    transition: all 0.3s ease-in-out;
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
    border-radius: 10px !important;
    font-weight: 600 !important;
    background-color: #52b788 !important;
    color: white !important;
}
button:hover {
    background-color: #40916c !important;
}

/* Logo + Title */
.logo {
    display: block;
    margin: auto;
    width: 130px;
}
.title-image {
    display: block;
    margin: 10px auto 25px;
    width: 350px;
}

/* Entry Icons */
.entry-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 80px;
    height: 80vh;
}
.entry-icon {
    text-align: center;
    cursor: pointer;
    transition: 0.3s;
}
.entry-icon img {
    width: 130px;
    height: 130px;
    border-radius: 50%;
    border: 3px solid #2d6a4f;
}
.entry-icon:hover {
    transform: scale(1.1);
}
.entry-icon p {
    margin-top: 10px;
    font-size: 20px;
    font-weight: bold;
    color: #1b4332;
}

/* Add-ons */
.addon-space {
    display: flex;
    justify-content: center;
    gap: 25px;
    margin-top: 40px;
}
.addon-space img {
    width: 120px;
    height: auto;
    border-radius: 10px;
    cursor: pointer;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -------------------------------
# FILE HANDLING
# -------------------------------
user_file = "users.csv"
expected_cols = ["Name", "Email", "Password", "Height", "Weight", "Gender", "Activity", "Goal"]

if not os.path.exists(user_file):
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

# -------------------------------
# LOGIN & SIGNUP
# -------------------------------
def signup_page():
    st.image("logo.png", width=130)
    st.image("title.png", width=330)
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
                "Name": name,
                "Email": email,
                "Password": password,
                "Height": height,
                "Weight": weight,
                "Gender": gender,
                "Activity": activity,
                "Goal": goal
            })

    st.markdown("---")
    if st.button("🔑 Already have an account? Login"):
        st.session_state.page = "login"

def login_page():
    st.image("logo.png", width=130)
    st.image("title.png", width=330)
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
    if st.button("📝 Don’t have an account? Sign Up"):
        st.session_state.page = "signup"

# -------------------------------
# FEATURES
# -------------------------------
def water_tracker():
    st.title("💧 Water Tracker")
    water_goal = st.number_input("Enter your daily goal (liters):", min_value=0.5, max_value=10.0, step=0.5)
    consumed = st.number_input("Enter water consumed so far (liters):", min_value=0.0, max_value=water_goal, step=0.1)
    progress = (consumed / water_goal) * 100 if water_goal > 0 else 0
    st.progress(progress / 100)
    st.info(f"💦 You’ve reached {progress:.1f}% of your daily goal!")

def nutrition_page():
    st.title("🍎 Nutrition & Diet Plan")
    st.write("Track your daily calories and maintain a healthy diet.")
    calories = st.number_input("Calories consumed today:", min_value=0)
    goal = st.number_input("Target daily calories:", min_value=1000)
    st.progress(min(calories / goal, 1.0))
    st.info(f"🔥 {calories} / {goal} kcal")

def goal_progress():
    st.title("🎯 Goal Progress")
    st.write("Visualize your weekly progress.")
    dates = pd.date_range(datetime.datetime.now() - datetime.timedelta(days=6), datetime.datetime.now())
    progress = [random]()
