# main.py
import streamlit as st
import pandas as pd
import datetime
import os
import random

# -------------------------------
# Basic files & constants
# -------------------------------
USERS_FILE = "users.csv"
DATA_FILE = "progress.csv"
STREAK_FILE = "streak.csv"

# Ensure user file exists
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["name","email","password","height_cm","weight_kg","gender","activity","goal","created_at"]).to_csv(USERS_FILE, index=False)
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Email", "Calories", "Water(L)", "GoalWeight"]).to_csv(DATA_FILE, index=False)
if not os.path.exists(STREAK_FILE):
    pd.DataFrame(columns=["Date", "Email"]).to_csv(STREAK_FILE, index=False)

# -------------------------------
# PAGE CONFIG - use logo.png as page_icon
# -------------------------------
# NOTE: Streamlit accepts a local path or URL for page_icon. Make sure logo.png is committed to your repo.
st.set_page_config(page_title="NuTraDaily", page_icon="logo.png", layout="wide")

# -------------------------------
# CUSTOM CSS: background.jpg and styling
# -------------------------------
css = f"""
<style>
/* full app background */
[data-testid="stAppViewContainer"] {{
    background: url('background.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    font-family: 'Poppins', sans-serif;
    color: #0f5132;
}}

/* translucent cards */
.stImage, [data-testid="stDataFrame"], .stPlotlyChart {{
    background: rgba(255,255,255,0.85);
    border-radius: 12px;
    padding: 10px;
}}

/* buttons */
button {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    background-color: #2d6a4f !important;
    color: white !important;
}}
button:hover {{
    background-color: #1b4332 !important;
}}

/* sidebar gradient */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, rgba(30,70,60,0.95), rgba(20,40,35,0.95));
    color: #f1faee;
}}

/* hide default menu (optional) */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# -------------------------------
# Helper functions for users
# -------------------------------
def load_users():
    return pd.read_csv(USERS_FILE)

def save_user(user_dict):
    df = load_users()
    df = pd.concat([df, pd.DataFrame([user_dict])], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)

def authenticate(email, password):
    df = load_users()
    match = df[(df["email"] == email) & (df["password"] == password)]
    if not match.empty:
        return match.iloc[0].to_dict()
    return None

# -------------------------------
# Session state init
# -------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = None

# -------------------------------
# Top title image (title.png)
# -------------------------------
# If you don't want title image to appear on every page, move this inside "Home" block
st.image("title.png", width=380)

# -------------------------------
# Sidebar: show logo and selectbox nav (click-to-open)
# -------------------------------
st.sidebar.image("logo.png", width=160)
menu = st.sidebar.selectbox("Navigate", [
    "Home",
    "Nutrition & Diet",
    "Water Tracker",
    "Food Photo",
    "Goal Progress",
    "Weekly Report",
    "Daily Streak",
    "Account"
])

# -------------------------------
# AUTH UI: Sign Up / Login / Logout
# -------------------------------
st.sidebar.markdown("---")
if not st.session_state.auth:
    auth_mode = st.sidebar.selectbox("Account action", ["Login", "Sign Up"])
    if auth_mode == "Sign Up":
        st.sidebar.markdown("### Create an account")
        su_name = st.sidebar.text_input("Full name", key="su_name")
        su_email = st.sidebar.text_input("Email", key="su_email")
        su_password = st.sidebar.text_input("Password", type="password", key="su_password")
        su_height = st.sidebar.number_input("Height (cm)", 100, 250, key="su_height")
        su_weight = st.sidebar.number_input("Weight (kg)", 20, 300, key="su_weight")
        su_gender = st.sidebar.selectbox("Gender", ["Prefer not to say","Male","Female","Other"], key="su_gender")
        su_activity = st.sidebar.selectbox("Activity level", ["Low","Moderate","High"], key="su_activity")
        # toggle-like goal choice using radio or selectbox
        su_goal = st.sidebar.selectbox("Goal", ["Maintain weight","Weight loss","Weight gain","Build muscle"], key="su_goal")
        if st.sidebar.button("Sign Up"):
            if su_name.strip()=="" or su_email.strip()=="" or su_password.strip()=="":
                st.sidebar.error("Name, Email and Password are required.")
            else:
                users = load_users()
                if su_email in users["email"].values:
                    st.sidebar.warning("Email already registered. Please log in.")
                else:
                    user_dict = {
                        "name": su_name,
                        "email": su_email,
                        "password": su_password,   # NOTE: plain-text; consider hashing for production
                        "height_cm": su_height,
                        "weight_kg": su_weight,
                        "gender": su_gender,
                        "activity": su_activity,
                        "goal": su_goal,
                        "created_at": datetime.datetime.utcnow().isoformat()
                    }
                    save_user(user_dict)
                    st.sidebar.success("Account created — now log in below.")
    else:
        st.sidebar.markdown("### Login")
        li_email = st.sidebar.text_input("Email", key="li_email")
        li_password = st.sidebar.text_input("Password", type="password", key="li_password")
        if st.sidebar.button("Login"):
            user = authenticate(li_email, li_password)
            if user:
                st.session_state.auth = True
                st.session_state.user = user
                st.sidebar.success(f"Welcome back, {user['name'].split()[0]}!")
            else:
                st.sidebar.error("Login failed — check email/password or sign up.")
else:
    st.sidebar.markdown(f"**Signed in as**\n\n**{st.session_state.user['name']}**\n\n{st.session_state.user['email']}")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.session_state.user = None
        st.sidebar.info("Logged out.")

st.sidebar.markdown("---")
st.sidebar.markdown("Made with 💚 — NuTraDaily")

# -------------------------------
# Helper: require login decorator-like
# -------------------------------
def require_login():
    if not st.session_state.auth:
        st.warning("Please sign up / login from the sidebar to access your dashboard.")
        st.stop()

# -------------------------------
# Pages
# -------------------------------
if menu == "Home":
    st.title("Welcome 🌿")
    st.markdown("**NuTraDaily** — your daily nutrition & habit tracker. Sign up or log in from the left to start.")
    st.image("logo.png", width=240)
    st.markdown("---")
    st.write("Quick tips:")
    st.write("- Keep your profile updated in the sidebar signup form.")
    st.write("- Your login & password are stored in the app's `users.csv` file (repo).")

elif menu == "Nutrition & Diet":
    require_login()
    st.title("🍎 Nutrition & Diet")
    # show saved profile from sign up
    user = st.session_state.user
    st.subheader(f"Hello, {user['name'].split()[0]} — here's your profile")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Height (cm)**:", user.get("height_cm"))
        st.write("**Weight (kg)**:", user.get("weight_kg"))
        st.write("**Gender**:", user.get("gender"))
    with col2:
        st.write("**Activity**:", user.get("activity"))
        st.write("**Goal**:", user.get("goal"))

    # Allow editing (save back to users.csv)
    if st.button("Edit profile"):
        users = load_users()
        idx = users.index[users["email"] == user["email"]][0]
        # simple inline edits
        new_weight = st.number_input("Update weight (kg)", 20, 300, value=float(user.get("weight_kg", 70)))
        new_activity = st.selectbox("Update activity", ["Low","Moderate","High"], index=["Low","Moderate","High"].index(user.get("activity","Moderate")))
        new_goal = st.selectbox("Update goal", ["Maintain weight","Weight loss","Weight gain","Build muscle"], index=["Maintain weight","Weight loss","Weight gain","Build muscle"].index(user.get("goal","Maintain weight")))
        if st.button("Save changes"):
            users.loc[idx, "weight_kg"] = new_weight
            users.loc[idx, "activity"] = new_activity
            users.loc[idx, "goal"] = new_goal
            users.to_csv(USERS_FILE, index=False)
            st.success("Profile updated. Refresh or re-login to see updated values.")
    st.markdown("---")

    # Calorie calc (basic)
    age = st.number_input("Age (years)", 10, 100, 25)
    height = float(user.get("height_cm", 170))
    weight = float(user.get("weight_kg", 70))
    gender = user.get("gender", "Prefer not to say")
    activity = st.selectbox("Activity level for calculation", ["Low","Moderate","High"], index=["Low","Moderate","High"].index(user.get("activity","Moderate")))
    if gender == "Male":
        bmr = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age)
    elif gender == "Female":
        bmr = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age)
    else:
        # approximate average
        bmr = 450 + (11 * weight) + (4 * height) - (5.0 * age)
    activity_factor = {"Low":1.2,"Moderate":1.55,"High":1.9}[activity]
    daily_calories = round(bmr * activity_factor)
    st.success(f"Estimated daily calories: **{daily_calories} kcal**")

    # Save today's progress button
    if st.button("Save today's baseline"):
        df = pd.read_csv(DATA_FILE)
        row = {"Date": str(datetime.date.today()), "Email": user["email"], "Calories": daily_calories, "Water(L)": 0, "GoalWeight": user.get("weight_kg")}
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("Saved today's baseline to your progress file.")

elif menu == "Water Tracker":
    require_login()
    st.title("💧 Water Tracker")
    weight = float(st.session_state.user.get("weight_kg", 65))
    water_goal = round(weight * 35 / 1000, 2)  # liters
    intake = st.slider("Water consumed today (L)", 0.0, 5.0, 1.0, 0.1)
    progress = min(intake / water_goal, 1.0) if water_goal>0 else 0
    st.progress(progress)
    st.write(f"You drank **{intake:.1f} L** / **{water_goal:.1f} L**")
    if st.button("Save water intake"):
        df = pd.read_csv(DATA_FILE)
        row = {"Date": str(datetime.date.today()), "Email": st.session_state.user["email"], "Calories": None, "Water(L)": intake, "GoalWeight": st.session_state.user.get("weight_kg")}
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("Saved water intake.")

elif menu == "Food Photo":
    require_login()
    st.title("📸 Upload Meal Photo")
    uploaded = st.file_uploader("Upload food image", type=["png","jpg","jpeg"])
    if uploaded:
        st.image(uploaded, use_column_width=True)
        st.success("Photo uploaded (shows only locally in this session).")

elif menu == "Goal Progress":
    require_login()
    st.title("🎯 Goal Progress")
    current = st.number_input("Current weight (kg)", 20, 300, float(st.session_state.user.get("weight_kg",70)))
    goal = st.number_input("Goal weight (kg)", 20, 300, float(st.session_state.user.get("weight_kg",70)))
    weekly_loss = st.slider("Expected weekly change (kg)", 0.1, 2.0, 0.5)
    diff = abs(current - goal)
    weeks_needed = diff / weekly_loss if weekly_loss else 0
    st.info(f"Estimated time to reach goal: **{weeks_needed:.1f} weeks**")

elif menu == "Weekly Report":
    require_login()
    st.title("📊 Weekly Report")
    df = pd.read_csv(DATA_FILE)
    df = df[df["Email"] == st.session_state.user["email"]]
    if df.empty:
        st.warning("No data yet. Save some entries from Nutrition or Water pages.")
    else:
        df["Date"] = pd.to_datetime(df["Date"])
        st.dataframe(df.sort_values("Date").tail(14))

elif menu == "Daily Streak":
    require_login()
    st.title("🔥 Daily Streak")
    s_df = pd.read_csv(STREAK_FILE)
    email = st.session_state.user["email"]
    today = str(datetime.date.today())
    user_s = s_df[s_df["Email"]==email]
    if st.button("Mark Today as Done"):
        if not ((s_df["Date"]==today) & (s_df["Email"]==email)).any():
            s_df = pd.concat([s_df, pd.DataFrame([{"Date":today, "Email": email}])], ignore_index=True)
            s_df.to_csv(STREAK_FILE, index=False)
            st.success("Marked today ✅")
        else:
            st.info("Already marked today.")
    # compute streaks
    user_s = s_df[s_df["Email"]==email].copy()
    if user_s.empty:
        st.warning("No streaks yet — mark today to begin!")
    else:
        user_s["Date"] = pd.to_datetime(user_s["Date"])
        user_s = user_s.sort_values("Date")
        current_streak = best_streak = 1
        for i in range(1, len(user_s)):
            if (user_s["Date"].iloc[i] - user_s["Date"].iloc[i-1]).days == 1:
                current_streak += 1
                best_streak = max(best_streak, current_streak)
            else:
                current_streak = 1
        st.subheader(f"Current streak: {current_streak} days")
        st.subheader(f"Best streak: {best_streak} days")

elif menu == "Account":
    if not st.session_state.auth:
        st.info("Use the sidebar to sign up or log in.")
    else:
        st.title("Account")
        user = st.session_state.user
        st.write("Name:", user["name"])
        st.write("Email:", user["email"])
        st.write("Height (cm):", user.get("height_cm"))
        st.write("Weight (kg):", user.get("weight_kg"))
        st.write("Activity:", user.get("activity"))
        st.write("Goal:", user.get("goal"))
        if st.button("Delete my account (danger)"):
            df = load_users()
            df = df[df["email"] != user["email"]]
            df.to_csv(USERS_FILE, index=False)
            st.success("Account removed. Please refresh and sign up again if needed.")
            st.session_state.auth = False
            st.session_state.user = None
