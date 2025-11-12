# main.py
import streamlit as st
import pandas as pd
import os
import base64
import time
import datetime
import random
import matplotlib.pyplot as plt

# -------------------------
# Helpers: base64 & safe file init
# -------------------------
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

# -------------------------
# Page config
# -------------------------
favicon = "logo.png" if os.path.exists("logo.png") else "🥬"
st.set_page_config(page_title="NuTraDaily", page_icon=favicon, layout="wide")

# -------------------------
# CSS - professional, readable
# -------------------------
bg_css = f'background: url("data:image/jpg;base64,{BG_B64}") center/cover fixed;' if BG_B64 else ""
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    {bg_css}
    font-family: 'Inter', 'Poppins', sans-serif;
    color: #072b22;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #144b3a 0%, #1f6b53 100%);
    color: #f1fbf7;
}}
[data-testid="stSidebar"] .css-1d391kg, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {{
    color: #f1fbf7 !important;
}}

/* Panels and forms */
.panel {{
    background: rgba(255,255,255,0.92);
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 8px 28px rgba(10,10,10,0.08);
}}
.center-box {{
    display:flex;
    justify-content:center;
    align-items:center;
    width:100%;
    margin-top: 28px;
    margin-bottom: 28px;
}}
.form-card {{
    width: 420px;
}}

/* Buttons */
.btn-main {{
    background-color: #1f6b53;
    color: #fff;
    padding: 10px 24px;
    border-radius: 10px;
    font-weight: 600;
}}
.btn-main:hover {{ opacity:0.95; transform: translateY(-1px); }}

/* Header logo + title - centered (no spin) */
.logo-center {{
    display:block;
    margin: 6px auto 2px;
    width:160px;
}}
.title-center {{
    display:block;
    margin: 0 auto 12px;
    width:340px;
}}

/* Sidebar header inline (logo left, title right) */
.sidebar-header {{
    display:flex;
    align-items:center;
    gap:12px;
    padding: 8px 4px;
}}
.sidebar-logo {{
    width:46px;
    border-radius:6px;
}}
.sidebar-title {{
    width:160px;
}}

.nav-compact {{
    margin-top: 8px;
}}

/* Small responsive tweak */
@media(max-width:600px) {{
    .form-card {{ width: 92%; }}
    .logo-center {{ width:120px; }}
    .title-center {{ width:260px; }}
}}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Render helpers: logo/title safe display
# -------------------------
def render_logo_title_center():
    """Show logo above title centered (if images exist)"""
    html = ""
    if LOGO_B64:
        html += f'<img src="data:image/png;base64,{LOGO_B64}" class="logo-center"/>'
    if TITLE_B64:
        html += f'<img src="data:image/png;base64,{TITLE_B64}" class="title-center"/>'
    if html:
        st.markdown(html, unsafe_allow_html=True)
    else:
        # fallback text if images missing
        st.markdown("<h2 style='text-align:center; margin-bottom:4px;'>NuTraDaily</h2>", unsafe_allow_html=True)

def render_sidebar_header():
    """Small inline header in sidebar: logo left, title right."""
    if LOGO_B64 and TITLE_B64:
        st.sidebar.markdown(
            f"""
            <div class="sidebar-header">
                <img src="data:image/png;base64,{LOGO_B64}" class="sidebar-logo">
                <img src="data:image/png;base64,{TITLE_B64}" class="sidebar-title">
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<h3 style='color:#f1fbf7;'>NuTraDaily</h3>", unsafe_allow_html=True)

# -------------------------
# UX: show centered form card
# -------------------------
def show_centered_card(render_function):
    """Wrap form content in card centered on page."""
    st.markdown('<div class="center-box"><div class="panel form-card">', unsafe_allow_html=True)
    render_function()
    st.markdown('</div></div>', unsafe_allow_html=True)

# -------------------------
# Forms and pages
# -------------------------
def signup_form_inner():
    st.markdown("<h4 style='text-align:center; margin-bottom:6px;'>Create account</h4>", unsafe_allow_html=True)
    with st.form("signup_center"):
        name = st.text_input("Full name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0)
        weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=65.0)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        activity = st.selectbox("Activity level", ["Low", "Moderate", "High"])
        goal = st.selectbox("Goal", ["Weight Loss", "Weight Gain", "Maintenance"])
        submitted = st.form_submit_button("Sign Up", help="Create account")
        if submitted:
            if not (name and email and password):
                st.warning("Please provide name, email and password.")
            else:
                ok = save_user({
                    "Name": name, "Email": email, "Password": password,
                    "Height": height, "Weight": weight, "Gender": gender,
                    "Activity": activity, "Goal": goal
                })
                if ok:
                    # after sign-up show login form
                    st.session_state.show_signup = False
                    st.session_state.show_login = True

def login_form_inner():
    st.markdown("<h4 style='text-align:center; margin-bottom:6px;'>Log in</h4>", unsafe_allow_html=True)
    with st.form("login_center"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        submitted = st.form_submit_button("Login", help="Sign in")
        if submitted:
            if authenticate(email, password):
                st.success("Login successful.")
                st.session_state.logged_in = True
                st.session_state.current_user = email
            else:
                st.error("Invalid email or password.")

# About Us (replaces home)
def about_us_page():
    render_logo_title_center()       # logo above title at top of content
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write("## About Us")
    st.write("""
    **NuTraDaily** — simple, reliable wellness tracking.
    We help you log water, nutrition, and progress with a clean, privacy-first interface.
    
    • Track water intake\n
    • Set nutrition goals\n
    • Monitor streaks and progress
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Features
def water_page():
    render_logo_title_center()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write("## Water Tracker")
    goal = st.number_input("Daily goal (liters):", 0.5, 10.0, 2.0)
    consumed = st.number_input("Consumed today (liters):", min_value=0.0, max_value=goal, value=0.0)
    pct = (consumed / goal) * 100 if goal else 0
    st.progress(pct/100)
    st.info(f"{pct:.1f}% of daily goal")
    st.markdown('</div>', unsafe_allow_html=True)

def nutrition_page():
    render_logo_title_center()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write("## Nutrition & Diet")
    cal = st.number_input("Calories consumed today:", min_value=0, value=0)
    tgt = st.number_input("Target daily calories:", min_value=800, value=2000)
    st.progress(min(cal/tgt, 1.0))
    st.info(f"{cal} / {tgt} kcal")
    st.markdown('</div>', unsafe_allow_html=True)

def progress_page():
    render_logo_title_center()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write("## Progress")
    dates = pd.date_range(datetime.datetime.now() - datetime.timedelta(days=6), datetime.datetime.now())
    vals = [random.randint(40,100) for _ in dates]
    plt.figure(figsize=(6,3))
    plt.plot(dates, vals, marker='o')
    plt.title("Weekly progress")
    plt.tight_layout()
    st.pyplot(plt)
    st.markdown('</div>', unsafe_allow_html=True)

def streaks_page():
    render_logo_title_center()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write("## Streaks")
    days = random.randint(1,30)
    st.success(f"You're on a {days}-day streak! Keep it up.")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Entry screen: centered Login & SignUp compact controls
# -------------------------
def entry_screen():
    # show a single header (logo above title)
    render_logo_title_center()

    # center stacked action buttons
    st.markdown('<div class="center-box">', unsafe_allow_html=True)
    st.markdown('<div class="panel" style="width:420px; text-align:center;">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom:6px;'>Welcome — sign in or create an account</h3>", unsafe_allow_html=True)

    # two compact buttons stacked
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Login", key="entry_login"):
            st.session_state.show_login = True
            st.session_state.show_signup = False
    with col2:
        if st.button("Sign Up", key="entry_signup"):
            st.session_state.show_signup = True
            st.session_state.show_login = False

    # show whichever form is toggled (centered in the same card)
    if st.session_state.get("show_login"):
        st.markdown("<hr>", unsafe_allow_html=True)
        login_form_inner()
    if st.session_state.get("show_signup"):
        st.markdown("<hr>", unsafe_allow_html=True)
        signup_form_inner()

    st.markdown('</div></div>', unsafe_allow_html=True)

# -------------------------
# Sidebar header (logo left + title right) + nav
# -------------------------
def sidebar_and_nav():
    render_sidebar_header()
    st.sidebar.markdown('<div class="nav-compact" />', unsafe_allow_html=True)
    return st.sidebar.radio("Navigate", ["About Us", "Nutrition", "Water", "Progress", "Streaks"])

# -------------------------
# Main flow & routing
# -------------------------
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# If logged in => show dashboard with sidebar header
if st.session_state.logged_in:
    choice = sidebar_and_nav()
    # Always show header on content pages (logo above title)
    if choice == "About Us":
        about_us_page()
    elif choice == "Nutrition":
        nutrition_page()
    elif choice == "Water":
        water_page()
    elif choice == "Progress":
        progress_page()
    elif choice == "Streaks":
        streaks_page()

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.show_login = False
        st.session_state.show_signup = False
        st.experimental_rerun()

# Not logged in => show entry screen (centered)
else:
    # render just one centered header + compact actions
    entry_screen()

# -------------------------
# End
# -------------------------
