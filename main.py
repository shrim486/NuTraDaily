import streamlit as st
import pandas as pd
import os
import base64
import datetime
import random
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Helpers
# -------------------------------------------------------
def file_to_base64(path):
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        return None
    return None

LOGO_B64 = file_to_base64("logo.png")
TITLE_B64 = file_to_base64("title.png")
BG_B64 = file_to_base64("background.jpg")

USERS_CSV = "users.csv"
USER_COLS = ["Name", "Email", "Password", "Height", "Weight", "Gender", "Activity", "Goal"]

def ensure_users_file():
    if not os.path.exists(USERS_CSV):
        pd.DataFrame(columns=USER_COLS).to_csv(USERS_CSV, index=False)
    else:
        try:
            df = pd.read_csv(USERS_CSV)
            if list(df.columns) != USER_COLS:
                pd.DataFrame(columns=USER_COLS).to_csv(USERS_CSV, index=False)
        except Exception:
            pd.DataFrame(columns=USER_COLS).to_csv(USERS_CSV, index=False)

ensure_users_file()

def load_users():
    return pd.read_csv(USERS_CSV)

def save_user(record):
    df = load_users()
    if record["Email"] in df["Email"].values:
        st.warning("Email already registered. Please log in.")
        return False
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(USERS_CSV, index=False)
    st.success("Account created — now log in.")
    return True

def authenticate(email, password):
    df = load_users()
    return not df[(df["Email"] == email) & (df["Password"] == password)].empty

# -------------------------------------------------------
# Streamlit page config
# -------------------------------------------------------
favicon = "logo.png" if os.path.exists("logo.png") else "💧"
st.set_page_config(page_title="NuTraDaily", page_icon=favicon, layout="wide")

# -------------------------------------------------------
# CSS - modern & smooth
# -------------------------------------------------------
bg_css = f'background: url("data:image/jpg;base64,{BG_B64}") center/cover fixed;' if BG_B64 else ""
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    {bg_css}
    font-family: 'Poppins', sans-serif;
    color: #073a2e;
}}

/* Fade + slide animation */
@keyframes fadeSlide {{
  0% {{ opacity: 0; transform: translateY(40px); }}
  100% {{ opacity: 1; transform: translateY(0); }}
}}

/* Logo + title animation */
.fade-in {{
  animation: fadeSlide 1s ease-out;
}}

.logo-center {{
    display:block;
    margin: 0 auto 0;
    width: 180px;
    animation: fadeSlide 1s ease-in-out;
}}
.title-center {{
    display:block;
    margin: 2px auto 12px;
    width: 360px;
    animation: fadeSlide 1.3s ease-in-out;
}}

.sidebar-header {{
    display:flex;
    align-items:center;
    gap:10px;
    padding: 10px 8px;
}}
.sidebar-logo {{
    width:55px;
    border-radius:8px;
}}
.sidebar-title {{
    width:180px;
}}

.panel {{
    background: rgba(255,255,255,0.9);
    border-radius: 12px;
    padding: 20px;
    animation: fadeSlide 1.1s ease-in-out;
}}
.center-box {{
    display:flex;
    justify-content:center;
    align-items:center;
    width:100%;
    margin-top: 30px;
}}
.form-card {{
    width: 420px;
}}

.btn-main {{
    background-color: #1f6b53;
    color: white;
    padding: 10px 24px;
    border-radius: 10px;
    font-weight: 600;
}}
.btn-main:hover {{
    opacity:0.9;
    transform: scale(1.02);
}}

.compact-btn {{
    width: 100%;
    padding: 8px 0;
    margin: 6px 0;
    font-weight: 600;
    border-radius: 10px;
    background-color: #1f6b53;
    color: white;
    border: none;
}}

@media(max-width:600px) {{
    .form-card {{ width: 90%; }}
    .logo-center {{ width:120px; }}
    .title-center {{ width:250px; }}
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# UI Components
# -------------------------------------------------------
def render_logo_title_center():
    html = ""
    if LOGO_B64:
        html += f'<img src="data:image/png;base64,{LOGO_B64}" class="logo-center"/>'
    if TITLE_B64:
        html += f'<img src="data:image/png;base64,{TITLE_B64}" class="title-center"/>'
    st.markdown(html or "<h2 style='text-align:center;'>NuTraDaily</h2>", unsafe_allow_html=True)

def render_sidebar_header():
    if LOGO_B64 and TITLE_B64:
        st.sidebar.markdown(
            f"""
            <div class="sidebar-header">
                <img src="data:image/png;base64,{LOGO_B64}" class="sidebar-logo">
                <img src="data:image/png;base64,{TITLE_B64}" class="sidebar-title">
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<h3>NuTraDaily</h3>", unsafe_allow_html=True)

# -------------------------------------------------------
# Forms
# -------------------------------------------------------
def signup_form():
    with st.form("signup_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        height = st.number_input("Height (cm)", 50.0, 250.0, 170.0)
        weight = st.number_input("Weight (kg)", 10.0, 300.0, 65.0)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        activity = st.selectbox("Activity", ["Low", "Moderate", "High"])
        goal = st.selectbox("Goal", ["Weight Loss", "Weight Gain", "Maintenance"])
        submitted = st.form_submit_button("Sign Up", use_container_width=True)
        if submitted:
            if not (name and email and password):
                st.warning("Please fill all fields.")
            else:
                if save_user({
                    "Name": name, "Email": email, "Password": password,
                    "Height": height, "Weight": weight,
                    "Gender": gender, "Activity": activity, "Goal": goal
                }):
                    st.session_state.show_signup = False
                    st.session_state.show_login = True

def login_form():
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            if authenticate(email, password):
                st.session_state.logged_in = True
                st.session_state.current_user = email
            else:
                st.error("Invalid email or password")

# -------------------------------------------------------
# Pages
# -------------------------------------------------------
def about_us_page():
    render_logo_title_center()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write("## About Us")
    st.write("""
    Welcome to **NuTraDaily**, your modern wellness companion.
    Our goal is to make hydration and nutrition tracking effortless and fun.  
    - 💧 Track water intake  
    - 🥗 Monitor daily nutrition  
    - 📊 View weekly progress  
    - 🔥 Maintain your wellness streaks  

    Designed with simplicity and privacy in mind.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

def water_page():
    render_logo_title_center()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write("## Water Tracker")
    goal = st.number_input("Daily goal (liters)", 0.5, 10.0, 2.0)
    consumed = st.number_input("Consumed today (liters)", 0.0, goal, 0.0)
    pct = (consumed / goal) * 100 if goal else 0
    st.progress(pct/100)
    st.info(f"{pct:.1f}% of daily goal")
    st.markdown('</div>', unsafe_allow_html=True)

def nutrition_page():
    render_logo_title_center()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write("## Nutrition")
    cal = st.number_input("Calories today", 0, 5000, 0)
    tgt = st.number_input("Target calories", 800, 4000, 2000)
    st.progress(min(cal/tgt, 1.0))
    st.info(f"{cal} / {tgt} kcal")
    st.markdown('</div>', unsafe_allow_html=True)

def progress_page():
    render_logo_title_center()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write("## Weekly Progress")
    dates = pd.date_range(datetime.datetime.now() - datetime.timedelta(days=6), datetime.datetime.now())
    vals = [random.randint(40,100) for _ in dates]
    plt.figure(figsize=(6,3))
    plt.plot(dates, vals, marker='o')
    plt.title("Weekly Performance")
    plt.tight_layout()
    st.pyplot(plt)
    st.markdown('</div>', unsafe_allow_html=True)

def streaks_page():
    render_logo_title_center()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write("## Streaks")
    days = random.randint(1,30)
    st.success(f"🔥 You’re on a {days}-day streak! Keep it up.")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------
# Entry screen
# -------------------------------------------------------
def entry_screen():
    render_logo_title_center()
    st.markdown('<div class="center-box fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="panel form-card" style="text-align:center;">', unsafe_allow_html=True)
    st.markdown("<h4>Welcome! Choose an option below</h4>", unsafe_allow_html=True)
    
    if st.button("Login", key="login_btn", use_container_width=True, type="primary"):
        st.session_state.show_login = True
        st.session_state.show_signup = False
    if st.button("Sign Up", key="signup_btn", use_container_width=True, type="primary"):
        st.session_state.show_signup = True
        st.session_state.show_login = False

    if st.session_state.get("show_login"):
        st.markdown("<hr>", unsafe_allow_html=True)
        login_form()
    if st.session_state.get("show_signup"):
        st.markdown("<hr>", unsafe_allow_html=True)
        signup_form()

    st.markdown('</div></div>', unsafe_allow_html=True)

# -------------------------------------------------------
# Sidebar & Navigation
# -------------------------------------------------------
def sidebar_and_nav():
    render_sidebar_header()
    st.sidebar.markdown("---")
    return st.sidebar.radio("Navigate", ["About Us", "Water", "Nutrition", "Progress", "Streaks"])

# -------------------------------------------------------
# State control & routing
# -------------------------------------------------------
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    choice = sidebar_and_nav()
    if choice == "About Us":
        about_us_page()
    elif choice == "Water":
        water_page()
    elif choice == "Nutrition":
        nutrition_page()
    elif choice == "Progress":
        progress_page()
    elif choice == "Streaks":
        streaks_page()

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        for key in ["logged_in", "show_login", "show_signup"]:
            st.session_state[key] = False
        st.experimental_rerun()
else:
    entry_screen()
