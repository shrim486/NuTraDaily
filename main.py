# main.py
import streamlit as st
import pandas as pd
import datetime
import os
import time
import random
import base64
import matplotlib.pyplot as plt

# ---------------------------
# Utilities: base64 embed local images (works on Streamlit Cloud)
# ---------------------------
def file_to_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

LOGO_B64 = file_to_base64("logo.png")
TITLE_B64 = file_to_base64("title.png")
BG_B64 = file_to_base64("background.jpg")

# ---------------------------
# Page config (favicon uses logo file if available)
# ---------------------------
favicon = "logo.png" if os.path.exists("logo.png") else "🥬"
st.set_page_config(page_title="NuTraDaily", page_icon=favicon, layout="wide")

# ---------------------------
# CSS: background, panels, rotating logo animation, form card
# ---------------------------
bg_style = f'background: url("data:image/jpg;base64,{BG_B64}") center/cover fixed;' if BG_B64 else ""
css = f"""
<style>
{{
}}
[data-testid="stAppViewContainer"] {{
    {bg_style}
    font-family: 'Poppins', sans-serif;
    color: #073b2a;
}}
/* semi-transparent panel for forms/content so text is readable */
.panel {{
    background: rgba(255,255,255,0.88);
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 6px 22px rgba(0,0,0,0.12);
}}
/* center forms on view */
.center-box {{
    display:flex;
    justify-content:center;
    align-items:center;
    width:100%;
    margin-top: 24px;
}}
.form-card {{
    width: 420px;
}}
/* stacked small buttons */
.stack-btns {{
    display:flex;
    flex-direction:column;
    gap:10px;
    align-items:center;
    margin-top:18px;
}}
.small-btn {{
    padding:10px 18px;
    border-radius:10px;
    background:#2d6a4f;
    color:white;
    font-weight:600;
    cursor:pointer;
}}
.small-btn:hover {{ opacity:0.9; }}

/* logo & title center */
.logo-center {{ display:block; margin: 12px auto 6px; width:160px; }}
.title-center {{ display:block; margin:6px auto 18px; width:360px; }}

/* rotating spinner logo for loader */
.loader-wrap {{ display:flex; justify-content:center; align-items:center; height:260px; }}
@keyframes spin {{
  from {{ transform: rotate(0deg); }}
  to {{ transform: rotate(360deg); }}
}}
.spin-logo {{
  width: 180px;
  animation: spin 1.2s linear infinite;
}}

/* sidebar tweaks */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #1b4332 0%, #2d6a4f 100%);
    color: #f1faee;
}}
[data-testid="stSidebar"] .css-1d391kg {{ color: #f1faee; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ---------------------------
# Users file safe init
# ---------------------------
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
        st.warning("Email already exists — try logging in.")
        return False
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(USERS_CSV, index=False)
    st.success("Account created — you can now log in.")
    return True

def authenticate(email, password):
    df = load_users()
    return not df[(df["Email"]==email) & (df["Password"]==password)].empty

# ---------------------------
# Helper: show rotating logo loader (center)
# ---------------------------
def show_rotating_loader(duration=1.0):
    placeholder = st.empty()
    if LOGO_B64:
        placeholder.markdown(
            f'<div class="loader-wrap"><img class="spin-logo" src="data:image/png;base64,{LOGO_B64}"></div>',
            unsafe_allow_html=True
        )
        time.sleep(duration)
    else:
        with st.spinner("Loading..."):
            time.sleep(duration)
    placeholder.empty()

# ---------------------------
# UI: logo + title helper (centered, larger logo)
# ---------------------------
def show_logo_and_title(big_logo_width=160, title_width=360):
    if LOGO_B64:
        st.markdown(f'<img src="data:image/png;base64,{LOGO_B64}" class="logo-center" style="width:{big_logo_width}px;">', unsafe_allow_html=True)
    if TITLE_B64:
        st.markdown(f'<img src="data:image/png;base64,{TITLE_B64}" class="title-center" style="width:{title_width}px;">', unsafe_allow_html=True)

# ---------------------------
# Entry: compact stacked Login / Sign Up buttons -> expands forms in center
# ---------------------------
def entry_screen():
    show_logo_and_title()
    st.markdown("<h3 style='text-align:center; color:#073b2a;'>Welcome to NuTraDaily</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#073b2a;'>Login or sign up to start tracking</p>", unsafe_allow_html=True)

    # stacked buttons
    st.markdown('<div class="center-box"><div class="stack-btns">', unsafe_allow_html=True)
    col1, col2 = st.columns([1,1])
    # We'll place buttons centered — using session_state toggles
    if st.button("Login", key="btn_entry_login"):
        st.session_state.show_login = True
        st.session_state.show_signup = False
        show_rotating_loader(0.6)
    if st.button("Sign Up", key="btn_entry_signup"):
        st.session_state.show_signup = True
        st.session_state.show_login = False
        show_rotating_loader(0.6)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # show form card in center if toggled
    if st.session_state.get("show_login"):
        with st.container():
            st.markdown('<div class="center-box"><div class="panel form-card">', unsafe_allow_html=True)
            login_form()
            st.markdown('</div></div>', unsafe_allow_html=True)
    if st.session_state.get("show_signup"):
        with st.container():
            st.markdown('<div class="center-box"><div class="panel form-card">', unsafe_allow_html=True)
            signup_form()
            st.markdown('</div></div>', unsafe_allow_html=True)

# ---------------------------
# Forms (used both from entry and dedicated pages)
# ---------------------------
def signup_form():
    st.markdown("<h4 style='text-align:center;'>Create account</h4>", unsafe_allow_html=True)
    with st.form("signup_form_center"):
        name = st.text_input("Full name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0)
        weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=65.0)
        gender = st.selectbox("Gender", ["Male","Female","Other"])
        activity = st.selectbox("Activity level", ["Low","Moderate","High"])
        goal = st.selectbox("Goal", ["Weight Loss","Weight Gain","Maintenance"])
        submitted = st.form_submit_button("Sign Up")
        if submitted:
            if not (name and email and password):
                st.warning("Name, email, password required.")
            else:
                ok = save_user({
                    "Name": name, "Email": email, "Password": password,
                    "Height": height, "Weight": weight, "Gender": gender,
                    "Activity": activity, "Goal": goal
                })
                if ok:
                    st.session_state.show_signup = False
                    st.session_state.show_login = True  # encourage login

def login_form():
    st.markdown("<h4 style='text-align:center;'>Login</h4>", unsafe_allow_html=True)
    with st.form("login_form_center"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        submitted = st.form_submit_button("Login")
        if submitted:
            if authenticate(email, password):
                st.success("Login ok")
                st.session_state.logged_in = True
                st.session_state.current_user = email
                st.session_state.show_login = False
                show_rotating_loader(0.6)
            else:
                st.error("Invalid credentials")

# ---------------------------
# Post-login pages (dashboard + features)
# ---------------------------
def header_on_pages():
    # logo slightly smaller on dashboard header, still above title
    show_logo_and_title(big_logo_width=140, title_width=320)

def home_page():
    header_on_pages()
    st.title("Welcome back!")
    st.write("Your NuTraDaily dashboard.")
    st.markdown('<div class="panel">Explore features from the sidebar.</div>', unsafe_allow_html=True)

def water_page():
    header_on_pages()
    st.title("Water Tracker")
    goal = st.number_input("Daily goal (L):", 0.5, 10.0, 2.0)
    consumed = st.number_input("Consumed (L):", 0.0, goal, 0.0)
    pct = (consumed / goal) * 100 if goal else 0
    st.progress(pct/100)
    st.info(f"{pct:.1f}% of goal reached")

def nutrition_page():
    header_on_pages()
    st.title("Nutrition & Diet")
    cal = st.number_input("Calories today:", min_value=0, value=0)
    target = st.number_input("Target calories:", min_value=800, value=2000)
    st.progress(min(cal/target,1.0))
    st.info(f"{cal} / {target} kcal")

def progress_page():
    header_on_pages()
    st.title("Progress")
    dates = pd.date_range(datetime.datetime.now() - datetime.timedelta(days=6), datetime.datetime.now())
    vals = [random.randint(40,100) for _ in dates]
    plt.figure(figsize=(6,3))
    plt.plot(dates, vals, marker='o')
    plt.tight_layout()
    st.pyplot(plt)

def streaks_page():
    header_on_pages()
    st.title("Streaks")
    days = random.randint(1,30)
    st.success(f"You're on a {days}-day streak!")

# ---------------------------
# Session init & navigation
# ---------------------------
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "entry"

# Route
if st.session_state.logged_in:
    # dashboard
    header_on_pages()
    st.sidebar.title("Navigate")
    page_choice = st.sidebar.radio("", ["Home","Nutrition","Water","Progress","Streaks"])
    if page_choice == "Home":
        home_page()
    elif page_choice == "Nutrition":
        nutrition_page()
    elif page_choice == "Water":
        water_page()
    elif page_choice == "Progress":
        progress_page()
    elif page_choice == "Streaks":
        streaks_page()
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "entry"
        show_rotating_loader(0.5)
else:
    # entry + forms
    # small nav links (optional)
    if st.session_state.page == "entry":
        entry_screen()
    elif st.session_state.page == "login":
        # show small stacked buttons too
        show_logo_and_title()
        st.markdown('<div class="center-box"><div class="panel form-card">', unsafe_allow_html=True)
        login_form()
        st.markdown('</div></div>', unsafe_allow_html=True)
    elif st.session_state.page == "signup":
        show_logo_and_title()
        st.markdown('<div class="center-box"><div class="panel form-card">', unsafe_allow_html=True)
        signup_form()
        st.markdown('</div></div>', unsafe_allow_html=True)

# ---------------------------
# End of file
# ---------------------------
