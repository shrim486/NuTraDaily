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

# -------------------- Helpers --------------------
def file_to_base64(path):
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        return None
    return None

def save_profile_image(email, uploaded_file):
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
    b = read_profile_image_b64(email)
    if b:
        return b
    clip = file_to_base64("person_clipart.png")
    if clip:
        return clip
    return file_to_base64("default_avatar.png")

def pretty_date(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# -------------------- Assets --------------------
LOGO2_B64 = file_to_base64("logo (2).png") or file_to_base64("logo.png")
TITLE2_B64 = file_to_base64("title (2).png")
LOGIN_BG_B64 = file_to_base64("login.jpg")
GLOBAL_BG_B64 = file_to_base64("body.jpg") or file_to_base64("background2.jpg") or file_to_base64("background.jpg")

# -------------------- Data files --------------------
USERS_CSV = "users.csv"
USER_COLS = ["Name", "Email", "Password", "Height", "Weight", "Gender", "Activity", "Goal", "SignupDate", "ProfileS3Key"]
INTAKE_CSV = "intake.csv"
STREAKS_JSON = "streaks.json"

# -------------------- Local food DB --------------------
FOOD_DB = {
    "apple": {"cal": 52},
    "banana": {"cal": 96},
    "rice (100g)": {"cal": 130},
    "chicken breast (100g)": {"cal": 165},
    "egg (1 large)": {"cal": 78},
}

# -------------------- Ensure files --------------------
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

# -------------------- User utilities --------------------
def load_users():
    return pd.read_csv(USERS_CSV)

def save_user(record):
    df = load_users()
    if record["Email"] in df["Email"].values:
        st.warning("Email already registered. Please log in.")
        return False
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

# -------------------- Streamlit config --------------------
favicon = None
if LOGO2_B64:
    favicon = "logo (2).png" if os.path.exists("logo (2).png") else ("logo.png" if os.path.exists("logo.png") else "💧")
st.set_page_config(page_title="NuTraDaily", page_icon=favicon, layout="wide")

# -------------------- CSS (white text, responsive, no white columns) --------------------
GLOBAL_BG_CSS = f'background: url("data:image/jpg;base64,{GLOBAL_BG_B64}") center/cover fixed;' if GLOBAL_BG_B64 else ""
LOGIN_BG_CSS = f'background: url("data:image/jpg;base64,{LOGIN_BG_B64}") center/cover fixed;' if LOGIN_BG_B64 else ""

st.markdown(f"""
<style>
/* background */
[data-testid="stAppViewContainer"] {{
    {GLOBAL_BG_CSS}
    font-family: 'Poppins', sans-serif;
    color: #ffffff; /* white text globally */
}}

/* remove white column look */
div.block-container {{
    padding-top: 8px;
    padding-bottom: 8px;
}}
.section {{
    color: #fff;
}}
.panel, .about-panel, .profile-panel {{
    background: rgba(0,0,0,0.20) !important; /* semi-transparent to keep readability */
    box-shadow: none !important;
    border: none !important;
    padding: 12px 8px !important;
    color: #fff !important;
}}

/* center logo */
.logo-center {{
    display:block;
    margin: 8px auto 8px;
    width: 160px;
}}

/* compact form card centered with stacked buttons (responsive) */
.form-card-wrap {{
    display:flex;
    justify-content:center;
    align-items:center;
    width:100%;
    padding: 8px;
}}
.form-card {{
    width: 360px;
    max-width: 92%;
    background: transparent;
    border-radius:8px;
    padding: 6px;
    text-align:center;
    color: #fff;
}}

/* stacked buttons styling */
.st-btn {{
    display:block;
    width:100%;
    padding:12px 0;
    margin:10px 0;
    border-radius:8px;
    font-weight:700;
    background:#1f6b53;
    color:#fff;
    border:none;
}}

/* floating help button top-right */
.help-float {{
    position: fixed;
    right: 18px;
    top: 18px;
    z-index: 9999;
    background: rgba(255,255,255,0.06);
    color: #fff;
    border-radius:50%;
    width:42px;
    height:42px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight:700;
    border: 1px solid rgba(255,255,255,0.08);
    text-decoration:none;
}}

/* help overlay */
#help-modal {{
    position: fixed;
    right: 18px;
    top: 68px;
    z-index: 9998;
    width:320px;
    max-width:92%;
    background: rgba(0,0,0,0.85);
    border-radius:8px;
    padding:12px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.3);
    color: #fff;
    display:none;
}}
#help-modal:target {{
    display:block;
}}

/* glass UI */
.glass-wrap {{
    width:120px;
    height:220px;
    border: 2px solid rgba(255,255,255,0.15);
    border-radius: 6px;
    position:relative;
    overflow:hidden;
    background: linear-gradient(to top, rgba(255,255,255,0.02), rgba(255,255,255,0.03));
    box-shadow: inset 0 -30px 30px rgba(0,0,0,0.2);
}}
.glass-fill {{
    position:absolute;
    bottom:0;
    width:100%;
    height:0%;
    background: linear-gradient(to top, #28a6ff, #67d3ff);
    transition: height 0.5s ease;
}}

/* footer styling */
.footer {{
    font-size:12px;
    color:#ddd;
    text-align:center;
    margin-top:12px;
    padding-top:6px;
}}

/* responsive tweaks */
@media(min-width:1000px) {{
    .form-card {{ width: 420px; }}
}}
</style>
""", unsafe_allow_html=True)

# -------------------- Helper UI functions --------------------
def inject_login_bg():
    if LOGIN_BG_B64:
        st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            {LOGIN_BG_CSS} !important;
        }}
        </style>
        """, unsafe_allow_html=True)

def inject_global_bg():
    if GLOBAL_BG_B64:
        st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            {GLOBAL_BG_CSS} !important;
        }}
        </style>
        """, unsafe_allow_html=True)

def render_logo_top_center():
    if LOGO2_B64:
        st.markdown(f'<img src="data:image/png;base64,{LOGO2_B64}" class="logo-center"/>', unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align:center;color:#fff;'>NuTraDaily</h2>", unsafe_allow_html=True)

def render_help_float():
    st.markdown('<a href="#help" class="help-float">?</a>', unsafe_allow_html=True)
    help_html = """
    <div id="help-modal">
      <strong>How to sign up / login</strong>
      <ol style="padding-left:14px;margin-top:8px;color:#fff;">
        <li>Click <strong>Sign Up</strong>, fill fields & submit.</li>
        <li>You will be auto-logged in after sign up.</li>
        <li>To log in later, click <strong>Login</strong>.</li>
        <li>Change profile pic on Profile page.</li>
      </ol>
      <div style="text-align:right;"><a href="#" style="color:#9fe1ff;font-weight:700;">Close</a></div>
    </div>
    """
    st.markdown(help_html, unsafe_allow_html=True)

# -------------------- Forms --------------------
def signup_form():
    with st.form("signup_form", clear_on_submit=False):
        name = st.text_input("Full Name", key="su_name")
        email = st.text_input("Email", key="su_email")
        password = st.text_input("Password", type="password", key="su_pass")
        height = st.number_input("Height (cm)", 50.0, 250.0, 170.0, key="su_height")
        weight = st.number_input("Weight (kg)", 10.0, 300.0, 65.0, key="su_weight")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="su_gender")
        activity = st.selectbox("Activity", ["Low", "Moderate", "High"], key="su_activity")
        goal = st.selectbox("Goal", ["Weight Loss", "Weight Gain", "Maintenance"], key="su_goal")
        submitted = st.form_submit_button("Sign Up")
        if submitted:
            if not (name and email and password):
                st.warning("Please fill all fields.")
            else:
                if save_user({
                    "Name": name, "Email": email, "Password": password,
                    "Height": height, "Weight": weight,
                    "Gender": gender, "Activity": activity, "Goal": goal
                }):
                    st.session_state.current_user = email
                    st.session_state.logged_in = True
                    st.session_state.show_welcome = True
                    st.session_state.welcome_name = name
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
                rec = get_user_record(email)
                st.session_state.welcome_name = rec["Name"] if rec else email.split("@")[0]
                st.session_state.show_welcome = True
                if "login_time" not in st.session_state:
                    st.session_state.login_time = pretty_date(datetime.datetime.now())
                touch_user_streak(email)
                st.experimental_rerun()
            else:
                st.error("Invalid email or password")

# -------------------- Pages --------------------
def about_page():
    inject_global_bg()
    render_logo_top_center()
    render_help_float()
    st.markdown('<div class="about-panel">', unsafe_allow_html=True)
    st.write("## About Us")
    if os.path.exists("image.jpg"):
        img_b64 = file_to_base64("image.jpg")
        st.markdown(f'<img src="data:image/jpg;base64,{img_b64}" style="width:100%;border-radius:8px;margin-bottom:12px;">', unsafe_allow_html=True)
    st.text_area("Write About Us", value="Welcome to NuTraDaily — your modern wellness companion.", height=140, key="about_text")
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        st.markdown(f'<a href="tel:+918951200675" style="color:#fff;background:rgba(255,255,255,0.03);padding:8px 12px;border-radius:8px;text-decoration:none;">📞 Contact</a>', unsafe_allow_html=True)
    with c2:
        if st.button("Feedback", key="about_fb"):
            st.session_state.show_feedback = True
    with c3:
        st.markdown(f'<a href="mailto:arju2006nnn@gmail.com" style="color:#fff;background:rgba(255,255,255,0.03);padding:8px 12px;border-radius:8px;text-decoration:none;">✉️ Email</a>', unsafe_allow_html=True)
    if st.session_state.get("show_feedback"):
        with st.form("feedback_about"):
            st.text_input("Name (optional)")
            st.text_area("Feedback")
            if st.form_submit_button("Send"):
                st.success("Thanks — feedback received!")
                st.session_state.show_feedback = False
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">© NuTraDaily — All rights reserved</div>', unsafe_allow_html=True)

def profile_page():
    inject_global_bg()
    render_logo_top_center()
    render_help_float()
    st.markdown('<div class="profile-panel">', unsafe_allow_html=True)
    st.write("## Profile")
    if not st.session_state.get("logged_in"):
        st.info("Login to view or edit your profile.")
    else:
        email = st.session_state["current_user"]
        rec = get_user_record(email)
        if rec:
            # show title (2).png above profile pic in nav panel reflected here too
            if TITLE2_B64:
                st.markdown(f'<div style="text-align:center;margin-bottom:6px;"><img src="data:image/png;base64,{TITLE2_B64}" style="width:180px;"></div>', unsafe_allow_html=True)
            col1, col2 = st.columns([1,2])
            with col1:
                b64 = get_profile_b64(email)
                st.markdown(f'<img src="data:image/png;base64,{b64}" style="width:140px;border-radius:70px;">', unsafe_allow_html=True)
                uploaded = st.file_uploader("Change picture", type=["png","jpg","jpeg"], key="pf_upload")
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
    st.markdown('<div class="footer">© NuTraDaily — All rights reserved</div>', unsafe_allow_html=True)

def water_page():
    inject_global_bg()
    render_logo_top_center()
    render_help_float()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write("## Water Tracker")
    daily_goal_l = st.number_input("Daily goal (liters)", 0.5, 10.0, 2.0, step=0.25, key="water_goal")
    glass_ml = st.number_input("Glass size (ml)", 50, 1000, 250, step=50, key="glass_size")
    if "water_glasses" not in st.session_state:
        st.session_state.water_glasses = 0
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("Add glass"):
            st.session_state.water_glasses += 1
            st.toast("Added a glass! 💧")
    with c2:
        if st.button("Remove glass") and st.session_state.water_glasses > 0:
            st.session_state.water_glasses -= 1
    with c3:
        if st.button("Reset"):
            st.session_state.water_glasses = 0
    # compute fill
    consumed_l = (st.session_state.water_glasses * glass_ml) / 1000.0
    pct = min(consumed_l / daily_goal_l, 1.0) if daily_goal_l else 0.0
    filled_pct = int(min(100, (consumed_l / daily_goal_l) * 100)) if daily_goal_l else 0
    # glass visualization and stats (white text)
    html = f"""
    <div style="display:flex;gap:20px;align-items:flex-end;">
        <div class="glass-wrap" aria-hidden="true">
            <div class="glass-fill" style="height:{filled_pct}%;"></div>
        </div>
        <div style="color:#fff;">
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
    inject_global_bg()
    render_logo_top_center()
    render_help_float()
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
                cal = FOOD_DB[key]["cal"]
                st.write(f"**{q.title()}** — {cal} kcal")
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
    inject_global_bg()
    render_logo_top_center()
    render_help_float()
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
    inject_global_bg()
    render_logo_top_center()
    render_help_float()
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

# -------------------- Entry screen --------------------
def entry_screen():
    inject_login_bg()
    render_logo_top_center()
    render_help_float()
    st.markdown('<div class="form-card-wrap"><div class="form-card">', unsafe_allow_html=True)

    # Exclusive toggles: either Sign Up or Login visible
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "signup"  # default stacked view shows signup first

    # Toggle buttons (stacked & centered)
    col = st.columns([1])[0]
    with col:
        if st.button("Sign Up", key="toggle_signup", help="Show sign up"):
            st.session_state.auth_mode = "signup"
        if st.button("Login", key="toggle_login", help="Show login"):
            st.session_state.auth_mode = "login"

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    if st.session_state.auth_mode == "signup":
        signup_form()
    else:
        login_form()

    st.markdown('</div></div>', unsafe_allow_html=True)

# -------------------- Sidebar & routing --------------------
def sidebar_nav():
    # show title (2).png at top of sidebar
    if TITLE2_B64:
        st.sidebar.markdown(f'<div style="text-align:center;margin-top:10px;"><img src="data:image/png;base64,{TITLE2_B64}" style="width:180px;"></div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<h3 style='text-align:center;color:#fff;'>NuTraDaily</h3>", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    # profile block under title
    if st.session_state.get("logged_in"):
        email = st.session_state.get("current_user", "")
        b64 = get_profile_b64(email)
        rec = get_user_record(email)
        name = rec["Name"] if rec else email.split("@")[0]
        st.sidebar.image(f"data:image/png;base64,{b64}", width=72)
        st.sidebar.markdown(f"**{name}**  \n<small style='color:#ddd'>{email}</small>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<div style='color:#fff'>Not logged in</div>", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    choice = st.sidebar.selectbox("Navigate", ["About", "Profile", "Water", "Nutrition", "Progress", "Streaks"])
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        for k in ["logged_in", "show_welcome", "current_user", "login_time", "welcome_name"]:
            if k in st.session_state:
                del st.session_state[k]
        st.experimental_rerun()
    return choice

# -------------------- Session defaults --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = False

# welcome flash
if st.session_state.get("show_welcome"):
    name = st.session_state.get("welcome_name", "Friend")
    placeholder = st.empty()
    placeholder.markdown(f"<div style='text-align:center;margin-top:80px;font-size:40px;font-weight:900;color:#fff;'>✨ Welcome, {name}! ✨</div>", unsafe_allow_html=True)
    time.sleep(1.2)
    placeholder.empty()
    st.session_state.show_welcome = False

# main router
if st.session_state.logged_in:
    choice = sidebar_nav()
    if choice == "About":
        about_page()
    elif choice == "Profile":
        profile_page()
    elif choice == "Water":
        water_page()
    elif choice == "Nutrition":
        nutrition_page()
    elif choice == "Progress":
        progress_page()
    elif choice == "Streaks":
        streaks_page()
else:
    entry_screen()

