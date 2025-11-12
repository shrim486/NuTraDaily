import streamlit as st
import pandas as pd
import os
import base64
import datetime
import random
import matplotlib.pyplot as plt
import json
from io import BytesIO
import time

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

def save_profile_image(email, uploaded_file):
    """Save uploaded profile image as PNG in profiles folder keyed by email (safe filename)."""
    if not uploaded_file:
        return None
    os.makedirs("profiles", exist_ok=True)
    filename = f"profiles/{email.replace('@','__at__').replace('.','__dot__')}.png"
    with open(filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return filename

def read_profile_image_b64(email):
    filename = f"profiles/{email.replace('@','__at__').replace('.','__dot__')}.png"
    return file_to_base64(filename) if os.path.exists(filename) else None

def get_profile_b64(email):
    """Return user's profile image b64 or a clipart/default fallback."""
    # priority: user uploaded -> person clipart -> default avatar -> None
    b = read_profile_image_b64(email)
    if b:
        return b
    clip = file_to_base64("person_clipart.png")
    if clip:
        return clip
    return file_to_base64("default_avatar.png")

def pretty_date(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# --- Assets (center logo only; title only in sidebar) ---
LOGO_B64 = file_to_base64("logo.png")             # centered logo
SIDEBAR_TITLE_B64 = file_to_base64("title (2).png")  # navigation title above profile
# different backgrounds per area
LOGIN_BG_B64 = file_to_base64("login.jpg")
# Use body.jpg as global background for all non-login pages per request
ABOUT_BG_B64 = file_to_base64("body.jpg")
GLOBAL_BG_B64 = file_to_base64("body.jpg") or file_to_base64("background2.jpg") or file_to_base64("background.jpg")

USERS_CSV = "users.csv"
USER_COLS = ["Name", "Email", "Password", "Height", "Weight", "Gender", "Activity", "Goal", "SignupDate", "ProfileS3Key"]

# simple local DB for food lookup (extensible)
FOOD_DB = {
    "apple": {"cal": 52, "img": None},
    "banana": {"cal": 96, "img": None},
    "rice (100g)": {"cal": 130, "img": None},
    "chicken breast (100g)": {"cal": 165, "img": None},
    "egg (1 large)": {"cal": 78, "img": None},
}  # TODO: plug a real web API for images & extended db

INTAKE_CSV = "intake.csv"
STREAKS_JSON = "streaks.json"

def ensure_files():
    if not os.path.exists(USERS_CSV):
        pd.DataFrame(columns=USER_COLS).to_csv(USERS_CSV, index=False)
    else:
        try:
            df = pd.read_csv(USERS_CSV)
            for col in USER_COLS:
                if col not in df.columns:
                    df[col] = ""
            df.to_csv(USERS_CSV, index=False)
        except Exception:
            pd.DataFrame(columns=USER_COLS).to_csv(USERS_CSV, index=False)
    if not os.path.exists(INTAKE_CSV):
        pd.DataFrame(columns=["Email", "Date", "Item", "Calories"]).to_csv(INTAKE_CSV, index=False)
    if not os.path.exists(STREAKS_JSON):
        with open(STREAKS_JSON, "w") as f:
            json.dump({}, f)

ensure_files()

def load_users():
    return pd.read_csv(USERS_CSV)

def save_user(record):
    df = load_users()
    if record["Email"] in df["Email"].values:
        st.warning("Email already registered. Please log in.")
        return False
    # add signup date
    record["SignupDate"] = pretty_date(datetime.datetime.now())
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(USERS_CSV, index=False)
    st.success("Account created — now log in.")
    return True

def update_user(email, updates: dict):
    df = load_users()
    idx = df.index[df["Email"] == email].tolist()
    if not idx:
        st.error("User not found.")
        return False
    i = idx[0]
    for k, v in updates.items():
        if k in df.columns:
            df.at[i, k] = v
    df.to_csv(USERS_CSV, index=False)
    st.success("Profile updated.")
    return True

def authenticate(email, password):
    df = load_users()
    return not df[(df["Email"] == email) & (df["Password"] == password)].empty

def get_user_record(email):
    df = load_users()
    row = df[df["Email"] == email]
    if row.empty:
        return None
    return row.iloc[0].to_dict()

def add_intake(email, item, calories):
    df = pd.read_csv(INTAKE_CSV)
    new = {"Email": email, "Date": datetime.date.today().isoformat(), "Item": item, "Calories": calories}
    df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
    df.to_csv(INTAKE_CSV, index=False)

def get_today_intake(email):
    df = pd.read_csv(INTAKE_CSV)
    today = datetime.date.today().isoformat()
    user_df = df[(df["Email"] == email) & (df["Date"] == today)]
    if user_df.empty:
        return 0, []
    return user_df["Calories"].sum(), user_df.to_dict("records")

def load_streaks():
    with open(STREAKS_JSON, "r") as f:
        return json.load(f)

def save_streaks(d):
    with open(STREAKS_JSON, "w") as f:
        json.dump(d, f)

def touch_user_streak(email):
    d = load_streaks()
    now = datetime.date.today().isoformat()
    rec = d.get(email, {})
    if "first_active" not in rec:
        rec["first_active"] = now
    rec["last_active"] = now
    d[email] = rec
    save_streaks(d)

def days_since_first_active(email):
    d = load_streaks()
    rec = d.get(email, {})
    if "first_active" not in rec:
        return 0
    first = datetime.date.fromisoformat(rec["first_active"])
    return (datetime.date.today() - first).days + 1

# -------------------------------------------------------
# Streamlit page config
# -------------------------------------------------------
favicon = "logo.png" if os.path.exists("logo.png") else "💧"
st.set_page_config(page_title="NuTraDaily", page_icon=favicon, layout="wide")

# -------------------------------------------------------
# CSS - global; per-page backgrounds injected where needed
# -------------------------------------------------------
GLOBAL_BG_CSS = f'background: url("data:image/jpg;base64,{GLOBAL_BG_B64}") center/cover fixed;' if GLOBAL_BG_B64 else ""
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    {GLOBAL_BG_CSS}
    font-family: 'Poppins', sans-serif;
    color: #073a2e;
}}

/* Fade + slide animation */
@keyframes fadeSlide {{
  0% {{ opacity: 0; transform: translateY(40px); }}
  100% {{ opacity: 1; transform: translateY(0); }}
}}

/* Logo centered + spacing */
.logo-center {{
    display:block;
    margin: 12px auto 12px;
    width: 160px;
    animation: fadeSlide 1s ease-in-out;
}}

.sidebar-title-img {{
    display:block;
    margin: 6px auto 10px;
    width: 180px;
}}

.sidebar-header {{
    display:flex;
    align-items:center;
    gap:12px;
    padding: 8px;
    flex-direction:column; /* title stacked */
}}
.sidebar-avatar {{
    width:64px;
    height:64px;
    border-radius:50%;
    object-fit:cover;
    border: 2px solid rgba(0,0,0,0.06);
}}
.sidebar-name {{
    font-weight:700;
    margin-top:6px;
}}

/* panel */
.panel {{
    background: rgba(255,255,255,0.92);
    border-radius: 12px;
    padding: 18px;
    animation: fadeSlide 1.1s ease-in-out;
}}
.profile-panel {{
    background: linear-gradient(180deg, rgba(240,250,240,0.95), rgba(255,255,255,0.9));
    border-radius: 12px;
    padding: 14px;
    margin-top:12px;
}}
.about-panel {{
    background: linear-gradient(180deg, rgba(255,250,240,0.95), rgba(255,255,255,0.9));
    border-radius: 12px;
    padding: 14px;
    margin-top:12px;
}}

.center-box {{
    display:flex;
    justify-content:center;
    align-items:center;
    width:100%;
    margin-top: 18px;
}}
.form-card {{
    width: 320px; /* even shorter as requested */
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

.help-mark {{
    font-size:18px;
    background: rgba(255,255,255,0.85);
    border-radius:50%;
    padding:6px 8px;
    border:1px solid rgba(0,0,0,0.06);
}}
.footer {{
    font-size:12px;
    color:#666;
    text-align:center;
    margin-top:12px;
    padding-top:6px;
}}
.link-compact {{
    display:inline-block;
    padding:8px 12px;
    border-radius:8px;
    background:#f0f7ff;
    border:1px solid #d0e9ff;
    color:#0366d6;
    text-decoration:none;
    font-weight:600;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# UI Components
# -------------------------------------------------------
def inject_page_bg(b64):
    """Inject page-specific background override (temporary)."""
    if not b64:
        return
    css = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: url("data:image/jpg;base64,{b64}") center/cover fixed !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_logo_center_only():
    html = ""
    if LOGO_B64:
        html += f'<img src="data:image/png;base64,{LOGO_B64}" class="logo-center"/>'
    else:
        html += "<h2 style='text-align:center;'>NuTraDaily</h2>"
    st.markdown(html, unsafe_allow_html=True)

def render_sidebar_title_and_profile():
    # show title (2).png at top of sidebar (stacked)
    if SIDEBAR_TITLE_B64:
        st.sidebar.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{SIDEBAR_TITLE_B64}" class="sidebar-title-img"></div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<h3 style='text-align:center;'>NuTraDaily</h3>", unsafe_allow_html=True)

    # profile area if logged in
    if st.session_state.get("logged_in"):
        email = st.session_state.get("current_user", "")
        profile_b64 = get_profile_b64(email)
        user = get_user_record(email)
        name = user["Name"] if user is not None else email.split("@")[0]
        st.sidebar.markdown(
            f"""
            <div style="text-align:center;padding:8px 6px;">
                <img src="data:image/png;base64,{profile_b64}" class="sidebar-avatar"><br>
                <div class="sidebar-name">{name}</div>
                <div style="font-size:12px;color:#666;">{email}</div>
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------
# Forms (compact & centered)
# -------------------------------------------------------
def signup_form(compact=True):
    with st.form("signup_form", clear_on_submit=False):
        name = st.text_input("Full Name", key="su_name")
        email = st.text_input("Email", key="su_email")
        password = st.text_input("Password", type="password", key="su_pass")
        height = st.number_input("Height (cm)", 50.0, 250.0, 170.0, key="su_height")
        weight = st.number_input("Weight (kg)", 10.0, 300.0, 65.0, key="su_weight")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="su_gender")
        activity = st.selectbox("Activity", ["Low", "Moderate", "High"], key="su_activity")
        goal = st.selectbox("Goal", ["Weight Loss", "Weight Gain", "Maintenance"], key="su_goal")
        submitted = st.form_submit_button("Create account")
        if submitted:
            if not (name and email and password):
                st.warning("Please fill all fields.")
            else:
                if save_user({
                    "Name": name, "Email": email, "Password": password,
                    "Height": height, "Weight": weight,
                    "Gender": gender, "Activity": activity, "Goal": goal
                }):
                    # show welcome flash
                    st.session_state.current_user = email
                    st.session_state.logged_in = True
                    st.session_state.show_welcome = True
                    st.session_state.welcome_name = name
                    # ensure streak touched
                    touch_user_streak(email)
                    st.experimental_rerun()

def login_form():
    with st.form("login_form"):
        email = st.text_input("Email", key="li_email")
        password = st.text_input("Password", type="password", key="li_pass")
        submitted = st.form_submit_button("Login")
        if submitted:
            if authenticate(email, password):
                st.session_state.logged_in = True
                st.session_state.current_user = email
                # show welcome flash
                rec = get_user_record(email)
                st.session_state.welcome_name = rec["Name"] if rec else email.split("@")[0]
                st.session_state.show_welcome = True
                if "login_time" not in st.session_state:
                    st.session_state.login_time = pretty_date(datetime.datetime.now())
                touch_user_streak(email)
                st.experimental_rerun()
            else:
                st.error("Invalid email or password")

# -------------------------------------------------------
# Pages
# -------------------------------------------------------
def about_us_page():
    # about uses body.jpg which is already GLOBAL_BG_B64, but inject to be safe
    if ABOUT_BG_B64:
        inject_page_bg(ABOUT_BG_B64)
    render_logo_center_only()
    st.markdown('<div class="about-panel">', unsafe_allow_html=True)
    st.write("## About Us")
    # large image if exists (article size)
    if os.path.exists("image.jpg"):
        img_b64 = file_to_base64("image.jpg")
        st.markdown(f'<img src="data:image/jpg;base64,{img_b64}" style="width:100%;border-radius:8px;margin-bottom:12px;">', unsafe_allow_html=True)
    st.text_area("Write About Us", value="Welcome to NuTraDaily — your modern wellness companion.", height=140, key="about_text")
    # compact contact / feedback / email buttons
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        st.markdown('<a class="link-compact" href="tel:+911234567890">📞 Contact</a>', unsafe_allow_html=True)
    with c2:
        if st.button("Feedback", key="about_feedback"):
            st.session_state.show_feedback = True
    with c3:
        st.markdown('<a class="link-compact" href="mailto:hello@nutradaily.example">✉️ Email</a>', unsafe_allow_html=True)

    if st.session_state.get("show_feedback"):
        with st.form("feedback_about"):
            fb_name = st.text_input("Your name (optional)")
            fb_msg = st.text_area("Feedback")
            submitted = st.form_submit_button("Send feedback")
            if submitted:
                st.success("Thanks — feedback received!")
                st.session_state.show_feedback = False

    st.markdown('</div>', unsafe_allow_html=True)

    # profile edit below about us (distinct section)
    if st.session_state.get("logged_in"):
        st.markdown('<div class="profile-panel">', unsafe_allow_html=True)
        st.write("### Your Profile")
        email = st.session_state.get("current_user")
        rec = get_user_record(email)
        if rec:
            col1, col2 = st.columns([1,2])
            with col1:
                profile_b64 = get_profile_b64(email)
                st.markdown(f'<img src="data:image/png;base64,{profile_b64}" style="width:120px;border-radius:60px;">', unsafe_allow_html=True)
                uploaded = st.file_uploader("Change picture", type=["png","jpg","jpeg"], key="upload_pp")
                if uploaded:
                    saved = save_profile_image(email, uploaded)
                    if saved:
                        st.experimental_rerun()
            with col2:
                new_name = st.text_input("Name", value=rec["Name"])
                new_height = st.number_input("Height (cm)", 50.0, 250.0, float(rec.get("Height") if rec.get("Height") else 170.0))
                new_weight = st.number_input("Weight (kg)", 10.0, 300.0, float(rec.get("Weight") if rec.get("Weight") else 65.0))
                new_activity = st.selectbox("Activity", ["Low", "Moderate", "High"], index=["Low","Moderate","High"].index(rec.get("Activity")) if rec.get("Activity") in ["Low","Moderate","High"] else 1)
                if st.button("Save profile"):
                    update_user(email, {"Name": new_name, "Height": new_height, "Weight": new_weight, "Activity": new_activity})
        st.markdown('</div>', unsafe_allow_html=True)

    # copyright
    st.markdown('<div class="footer">© NuTraDaily — All rights reserved</div>', unsafe_allow_html=True)

def water_page():
    # ensure global body.jpg background applied
    if GLOBAL_BG_B64:
        inject_page_bg(GLOBAL_BG_B64)
    render_logo_center_only()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write("## Water Tracker")
    daily_goal_l = st.number_input("Daily goal (liters)", 0.5, 10.0, 2.0, step=0.25, key="water_goal")
    glass_ml = st.number_input("Glass size (ml)", 50, 1000, 250, step=50, key="glass_size")
    if "water_glasses" not in st.session_state:
        st.session_state.water_glasses = 0
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("Add glass"):
            st.session_state.water_glasses += 1
            st.toast("Added a glass! 💧")
    with col2:
        if st.button("Remove glass") and st.session_state.water_glasses > 0:
            st.session_state.water_glasses -= 1
    with col3:
        if st.button("Reset"):
            st.session_state.water_glasses = 0

    consumed_l = (st.session_state.water_glasses * glass_ml) / 1000.0
    pct = min(consumed_l / daily_goal_l, 1.0) if daily_goal_l else 0.0
    filled_pct = int(min(100, (consumed_l / daily_goal_l) * 100)) if daily_goal_l else 0
    html = f"""
    <div style="display:flex;gap:20px;align-items:flex-end;">
        <div class="glass-wrap">
            <div class="glass-fill" style="height:{filled_pct}%;"></div>
        </div>
        <div>
            <div style="font-weight:700;font-size:18px;">{consumed_l:.2f} L / {daily_goal_l:.2f} L</div>
            <div style="margin-top:6px;">Glasses: {st.session_state.water_glasses} ({glass_ml} ml each)</div>
            <div style="margin-top:6px;">Progress: {pct*100:.1f}%</div>
            </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    st.progress(pct)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">© NuTraDaily — All rights reserved</div>', unsafe_allow_html=True)

def nutrition_page():
    if GLOBAL_BG_B64:
        inject_page_bg(GLOBAL_BG_B64)
    render_logo_center_only()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write("## Nutrition")
    weight = st.number_input("Weight (kg)", 30.0, 300.0, 65.0, key="nut_weight")
    height = st.number_input("Height (cm)", 120.0, 250.0, 170.0, key="nut_height")
    age = st.number_input("Age (years)", 10, 100, 25, key="nut_age")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="nut_gender")
    activity = st.selectbox("Activity level", ["Sedentary", "Light", "Moderate", "Active", "Very Active"], index=2, key="nut_activity")
    activity_factors = {"Sedentary":1.2, "Light":1.375, "Moderate":1.55, "Active":1.725, "Very Active":1.9}
    bmr = 10*weight + 6.25*height - 5*age + (5 if gender == "Male" else -161 if gender == "Female" else -78)
    maintenance = bmr * activity_factors.get(activity, 1.55)
    gain = maintenance + 500
    loss = maintenance - 500
    st.markdown(f"**Estimated maintenance:** {int(maintenance)} kcal · **To gain:** {int(gain)} kcal · **To lose:** {int(loss)} kcal")
    st.write("### Daily calorie tracker")
    if not st.session_state.get("current_user"):
        st.info("Login to track your personal daily intake.")
    else:
        email = st.session_state["current_user"]
        target = st.number_input("Set daily calorie target", 800, 6000, 2000, key="cal_target")
        q = st.text_input("Search food (try 'apple', 'rice (100g)', etc.)", key="food_search")
        if st.button("Search food"):
            key = q.strip().lower()
            if key in FOOD_DB:
                food = FOOD_DB[key]
                cal = food["cal"]
                st.write(f"**{q.title()}** — {cal} kcal")
                col_a, col_b = st.columns([2,1])
                with col_b:
                    if st.button("Add to intake", key=f"add_{q}"):
                        add_intake(email, q, cal)
                        st.success(f"Added {q} — {cal} kcal")
            else:
                st.warning("Item not found in local DB. For web results, integrate a food API (TODO).")
        with st.form("manual_food"):
            item = st.text_input("Item name")
            kcal = st.number_input("Calories", 0, 5000, 100)
            ok = st.form_submit_button("Add manually")
            if ok and item:
                add_intake(email, item, kcal)
                st.success("Added.")

        today_sum, recs = get_today_intake(email)
        st.metric("Today's calories", f"{today_sum} kcal")
        st.progress(min(today_sum/target, 1.0))
        if recs:
            st.write("Entries:")
            for r in recs:
                st.write(f"- {r['Item']} — {r['Calories']} kcal")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">© NuTraDaily — All rights reserved</div>', unsafe_allow_html=True)

def progress_page():
    if GLOBAL_BG_B64:
        inject_page_bg(GLOBAL_BG_B64)
    render_logo_center_only()
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
    st.markdown('<div class="footer">© NuTraDaily — All rights reserved</div>', unsafe_allow_html=True)

def streaks_page():
    if GLOBAL_BG_B64:
        inject_page_bg(GLOBAL_BG_B64)
    render_logo_center_only()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write("## Streaks")
    if st.session_state.get("logged_in"):
        email = st.session_state["current_user"]
        days = days_since_first_active(email)
        st.success(f"🔥 You’re on a {days}-day streak! Keep it up.")
    else:
        st.info("Login to see your streak.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">© NuTraDaily — All rights reserved</div>', unsafe_allow_html=True)

# -------------------------------------------------------
# Entry screen (compact buttons + leftmost help '?')
# -------------------------------------------------------
def show_login_click():
    st.session_state.show_login = True
    st.session_state.show_signup = False

def show_signup_click():
    st.session_state.show_signup = True
    st.session_state.show_login = False

def entry_screen():
    # login background
    if LOGIN_BG_B64:
        inject_page_bg(LOGIN_BG_B64)
    render_logo_center_only()
    st.markdown('<div class="center-box fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="panel form-card" style="text-align:center;">', unsafe_allow_html=True)

    # layout: left small help, center form
    left_col, center_col, right_col = st.columns([0.2, 1, 0.2])
    with left_col:
        if st.button("?", key="help_q"):
            st.info("How to sign up / log in:\n\n1) Click Sign Up and fill fields. 2) After signing up you'll see a welcome greeting. 3) Login with email/password. If you forget password, re-register with another email.")
    with center_col:
        # dynamic greeting with name/time on main entry (centered)
        hour = datetime.datetime.now().hour
        if st.session_state.get("logged_in"):
            user = get_user_record(st.session_state["current_user"])
            uname = user["Name"] if user else st.session_state["current_user"].split("@")[0]
            if 0 <= hour < 12:
                greet = f"🌞 Hey {uname}, good morning!"
            elif 12 <= hour < 17:
                greet = f"🌤️ Hey {uname}, good afternoon!"
            else:
                greet = f"🌙 Hey {uname}, good evening!"
            st.markdown(f"<div style='text-align:center;font-size:20px;font-weight:700;'>{greet}</div>", unsafe_allow_html=True)
        else:
            if 0 <= hour < 12:
                st.markdown("<div style='text-align:center;font-size:20px;font-weight:700;'>🌞 Good morning! Welcome to NuTraDaily</div>", unsafe_allow_html=True)
            elif 12 <= hour < 17:
                st.markdown("<div style='text-align:center;font-size:20px;font-weight:700;'>🌤️ Good afternoon! Welcome to NuTraDaily</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='text-align:center;font-size:20px;font-weight:700;'>🌙 Good evening! Welcome to NuTraDaily</div>", unsafe_allow_html=True)

        # compact centered buttons
        st.write("")  # spacer
        btn_col1, btn_col2 = st.columns([1,1])
        with btn_col1:
            st.button("Login", key="login_btn_compact", on_click=show_login_click)
        with btn_col2:
            st.button("Sign Up", key="signup_btn_compact", on_click=show_signup_click)

        # show forms inline when toggled
        if st.session_state.get("show_login"):
            st.markdown("<hr>", unsafe_allow_html=True)
            login_form()
        if st.session_state.get("show_signup"):
            st.markdown("<hr>", unsafe_allow_html=True)
            signup_form()
    with right_col:
        st.write("")  # empty for symmetry

    st.markdown('</div></div>', unsafe_allow_html=True)

# -------------------------------------------------------
# Sidebar & Navigation
# -------------------------------------------------------
def sidebar_and_nav():
    render_sidebar_title_and_profile()
    st.sidebar.markdown("---")
    choice = st.sidebar.selectbox("Navigate", ["About Us", "Water", "Nutrition", "Progress", "Streaks"])
    return choice

# -------------------------------------------------------
# State control & routing
# -------------------------------------------------------
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_feedback" not in st.session_state:
    st.session_state.show_feedback = False
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = False

# If welcome flag is set, show big greeting then fade (quick)
if st.session_state.get("show_welcome"):
    # a quick centered big greeting before proceeding
    name = st.session_state.get("welcome_name", "Friend")
    placeholder = st.empty()
    placeholder.markdown(f"<div style='text-align:center;margin-top:80px;font-size:40px;font-weight:900;'>✨ Welcome, {name}! ✨</div>", unsafe_allow_html=True)
    # short pause to let it show
    time.sleep(1.5)
    placeholder.empty()
    st.session_state.show_welcome = False
    # proceed to app view (no rerun needed)

# main routing
if st.session_state.logged_in:
    email = st.session_state.current_user
    choice = sidebar_and_nav()

    # lightweight in-app reminder (UI only)
    now = datetime.datetime.now()
    if "last_reminder_minute" not in st.session_state:
        st.session_state.last_reminder_minute = -999
    if now.minute != st.session_state.last_reminder_minute and now.hour in range(8,22):
        st.info("Reminder: stay hydrated — add a glass in Water Tracker 💧")
        st.session_state.last_reminder_minute = now.minute

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
        for key in ["logged_in", "show_login", "show_signup", "current_user", "login_time", "welcome_name"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()
else:
    entry_screen()
