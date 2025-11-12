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

# Default images (fallback visuals)
LOGO_B64 = file_to_base64("logo.png")
TITLE_B64 = file_to_base64("title.png")
BG_B64 = file_to_base64("background2.jpg") or file_to_base64("background.jpg")
ABOUT_B64 = file_to_base64("image.jpg")

USERS_CSV = "users.csv"
USER_COLS = ["Name", "Email", "Password", "Height", "Weight", "Gender", "Activity", "Goal", "ProfilePic"]

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

def update_user(email, updated_info):
    df = load_users()
    df.loc[df["Email"] == email, list(updated_info.keys())] = list(updated_info.values())
    df.to_csv(USERS_CSV, index=False)

def authenticate(email, password):
    df = load_users()
    user = df[(df["Email"] == email) & (df["Password"] == password)]
    return user.iloc[0] if not user.empty else None

# -------------------------------------------------------
# Streamlit config
# -------------------------------------------------------
favicon = "logo.png" if os.path.exists("logo.png") else "💧"
st.set_page_config(page_title="NuTraDaily", page_icon=favicon, layout="wide")

# -------------------------------------------------------
# CSS - Refined Theme
# -------------------------------------------------------
bg_css = f'background: url("data:image/jpg;base64,{BG_B64}") center/cover fixed;' if BG_B64 else ""

st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    {bg_css}
    font-family: 'Poppins', sans-serif;
    color: #073a2e;
}}

.fadeSlide {{
  animation: fadeSlide 1s ease-in-out;
}}

@keyframes fadeSlide {{
  0% {{ opacity: 0; transform: translateY(30px); }}
  100% {{ opacity: 1; transform: translateY(0); }}
}}

.logo-title {{
  display:flex;
  justify-content:center;
  align-items:center;
  gap:4px;
  margin-bottom:15px;
}}
.logo-img {{
  width:65px;
}}
.title-img {{
  width:220px;
}}

.sidebar-header {{
  display:flex;
  align-items:center;
  gap:4px;
  padding: 10px 8px;
}}
.sidebar-logo {{
  width:45px;
  border-radius:8px;
}}
.sidebar-title {{
  width:130px;
}}
.profile-mini {{
  text-align:center;
  margin-top:8px;
}}
.profile-mini img {{
  width:60px;
  height:60px;
  border-radius:50%;
  object-fit:cover;
}}
.panel {{
  background: rgba(255,255,255,0.92);
  border-radius: 15px;
  padding: 25px;
  animation: fadeSlide 1.1s ease-in-out;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}}
.form-card {{
  width: 350px;
  margin:auto;
}}
.btn-main {{
  background-color: #1f6b53;
  color: white;
  border-radius: 10px;
  font-weight: 600;
  padding:10px 20px;
  border:none;
}}
.btn-main:hover {{
  opacity:0.9;
  transform: scale(1.02);
}}
textarea {{
  border-radius:10px !important;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# UI Components
# -------------------------------------------------------
def render_logo_title_center():
    html = '<div class="logo-title fadeSlide">'
    if LOGO_B64: html += f'<img src="data:image/png;base64,{LOGO_B64}" class="logo-img"/>'
    if TITLE_B64: html += f'<img src="data:image/png;base64,{TITLE_B64}" class="title-img"/>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def render_sidebar_header(user=None):
    st.sidebar.markdown(
        f"""
        <div class="sidebar-header">
            <img src="data:image/png;base64,{LOGO_B64}" class="sidebar-logo">
            <img src="data:image/png;base64,{TITLE_B64}" class="sidebar-title">
        </div>
        """, unsafe_allow_html=True
    )
    if user is not None:
        st.sidebar.markdown(
            f"""
            <div class="profile-mini">
                <img src="{user.get('ProfilePic', '')}" onerror="this.src='https://i.imgur.com/0y8Ftya.png'">
                <p><b>{user.get('Name', '')}</b></p>
            </div>
            """, unsafe_allow_html=True
        )

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
                save_user({
                    "Name": name, "Email": email, "Password": password,
                    "Height": height, "Weight": weight,
                    "Gender": gender, "Activity": activity, "Goal": goal,
                    "ProfilePic": ""
                })

def login_form():
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            user = authenticate(email, password)
            if user is not None:
                st.session_state.logged_in = True
                st.session_state.current_user = dict(user)
            else:
                st.error("Invalid email or password")

# -------------------------------------------------------
# Pages
# -------------------------------------------------------
def about_us_page(user):
    render_logo_title_center()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("About Us")

    if ABOUT_B64:
        st.image(f"data:image/jpg;base64,{ABOUT_B64}", use_container_width=True)

    st.text_area("About NuTraDaily", value="""NuTraDaily is your personalized nutrition and hydration companion.
We help you maintain healthy habits with simplicity and style.""", height=120)

    # Footer buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<a href="tel:+911234567890"><button class="btn-main">📞 Contact Us</button></a>',
            unsafe_allow_html=True)
    with col2:
        if st.button("💬 Feedback Form"):
            st.text_area("Write your feedback:")
            st.button("Submit Feedback", use_container_width=True)
    with col3:
        st.markdown(
            '<a href="mailto:nutradaily@gmail.com"><button class="btn-main">✉️ Email Us</button></a>',
            unsafe_allow_html=True)

    # Profile section
    st.markdown("---")
    st.subheader("Your Profile")
    st.write("Update or view your information below.")
    df = load_users()
    current = df[df["Email"] == user["Email"]].iloc[0].to_dict()

    uploaded = st.file_uploader("Upload Profile Picture", type=["jpg", "png"])
    pic_path = ""
    if uploaded:
        pic_path = f"profile_{user['Email'].split('@')[0]}.png"
        with open(pic_path, "wb") as f:
            f.write(uploaded.getbuffer())
        current["ProfilePic"] = pic_path
        update_user(user["Email"], {"ProfilePic": pic_path})
        st.success("Profile picture updated!")

    name = st.text_input("Name", current["Name"])
    height = st.number_input("Height (cm)", 50.0, 250.0, float(current["Height"]))
    weight = st.number_input("Weight (kg)", 10.0, 300.0, float(current["Weight"]))
    goal = st.selectbox("Goal", ["Weight Loss", "Weight Gain", "Maintenance"], index=["Weight Loss", "Weight Gain", "Maintenance"].index(current["Goal"]))
    if st.button("Save Changes", use_container_width=True):
        update_user(user["Email"], {"Name": name, "Height": height, "Weight": weight, "Goal": goal})
        st.success("Profile updated successfully!")

    st.markdown('</div>', unsafe_allow_html=True)

def water_page():
    render_logo_title_center()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Water Tracker")
    goal = st.number_input("Daily goal (liters)", 0.5, 10.0, 2.0)
    consumed = st.number_input("Consumed today (liters)", 0.0, goal, 0.0)
    pct = (consumed / goal) * 100 if goal else 0
    st.progress(pct/100)
    st.info(f"{pct:.1f}% of daily goal")
    st.markdown('</div>', unsafe_allow_html=True)

def nutrition_page():
    render_logo_title_center()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Nutrition Tracker")
    cal = st.number_input("Calories today", 0, 5000, 0)
    tgt = st.number_input("Target calories", 800, 4000, 2000)
    st.progress(min(cal/tgt, 1.0))
    st.info(f"{cal} / {tgt} kcal")
    st.markdown('</div>', unsafe_allow_html=True)

def progress_page():
    render_logo_title_center()
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Weekly Progress")
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
    st.subheader("Your Streaks")
    days = random.randint(1,30)
    st.success(f"🔥 You’re on a {days}-day streak! Keep it up.")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------
# Entry screen
# -------------------------------------------------------
def entry_screen():
    render_logo_title_center()
    st.markdown('<div class="panel form-card fadeSlide" style="text-align:center;">', unsafe_allow_html=True)
    st.markdown("<h4>Welcome! Choose an option below</h4>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", key="login_btn", use_container_width=True):
            st.session_state.show_login = True
            st.session_state.show_signup = False
    with col2:
        if st.button("Sign Up", key="signup_btn", use_container_width=True):
            st.session_state.show_signup = True
            st.session_state.show_login = False

    if st.session_state.get("show_login"):
        login_form()
    elif st.session_state.get("show_signup"):
        signup_form()

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------
# Sidebar & Navigation
# -------------------------------------------------------
def sidebar_and_nav(user):
    render_sidebar_header(user)
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
    user = st.session_state.current_user
    choice = sidebar_and_nav(user)
    if choice == "About Us":
        about_us_page(user)
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


