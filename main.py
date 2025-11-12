import streamlit as st
import pandas as pd
import os

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="NuTraDaily",
    page_icon="logo.png",
    layout="wide"
)

# -------------------------------
# BACKGROUND & STYLE
# -------------------------------
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: url("background.jpg") no-repeat center center fixed;
    background-size: cover;
    font-family: 'Poppins', sans-serif;
    color: #1b4332;
}

button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    background-color: #52b788 !important;
    color: white !important;
}
button:hover {
    background-color: #40916c !important;
}

.header {
    text-align: center;
    margin-top: 40px;
}
.corner-logo {
    position: absolute;
    top: 15px;
    left: 20px;
}
.corner-logo img {
    width: 80px;
}
.login-buttons {
    position: fixed;
    bottom: 25px;
    right: 25px;
    display: flex;
    flex-direction: column;
    gap: 10px;
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
if "page" not in st.session_state:
    st.session_state.page = "home"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = ""

# -------------------------------
# FUNCTIONS
# -------------------------------
def save_user(data):
    df = pd.read_csv(user_file)
    if data["Email"] in df["Email"].values:
        st.warning("⚠️ Email already registered. Please login.")
        return
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(user_file, index=False)
    st.success("✅ Account created successfully! You can now log in.")
    st.session_state.page = "login"

def verify_user(email, password):
    df = pd.read_csv(user_file)
    user = df[(df["Email"] == email) & (df["Password"] == password)]
    return not user.empty

# -------------------------------
# PAGES
# -------------------------------
def home_page():
    st.markdown('<div class="corner-logo"><img src="logo.png"></div>', unsafe_allow_html=True)
    st.markdown('<div class="header"><img src="title.png" height="90"></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; margin-top:20px;'>Welcome to NuTraDaily 🌿</h2>", unsafe_allow_html=True)
    st.info("Track your wellness, nutrition, and hydration goals — all in one place!")

    st.markdown(
        """
        <div style='margin-top:50px; text-align:center;'>
            <h3>🚀 Add-ons Coming Soon</h3>
            <img src='https://cdn-icons-png.flaticon.com/512/869/869636.png' width='150' style='margin:10px;'>
            <img src='https://cdn-icons-png.flaticon.com/512/1256/1256650.png' width='150' style='margin:10px;'>
            <img src='https://cdn-icons-png.flaticon.com/512/679/679922.png' width='150' style='margin:10px;'>
        </div>
        """,
        unsafe_allow_html=True
    )

def signup_page():
    st.title("🧾 Create Account")
    with st.form("signup_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        height = st.number_input("Height (cm)", 100, 250, 170)
        weight = st.number_input("Weight (kg)", 30, 200, 65)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"])
        goal = st.radio("Goal", ["Weight Loss", "Weight Gain", "Maintain"])
        submit = st.form_submit_button("Sign Up")

        if submit:
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
            else:
                st.warning("⚠️ Fill all required fields.")

def login_page():
    st.title("🔐 Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if verify_user(email, password):
                st.session_state.logged_in = True
                st.session_state.email = email
                st.success("✅ Logged in successfully!")
                st.session_state.page = "dashboard"
            else:
                st.error("❌ Invalid email or password.")

def dashboard_page():
    st.markdown('<div class="corner-logo"><img src="logo.png"></div>', unsafe_allow_html=True)
    st.markdown('<div class="header"><img src="title.png" height="90"></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>Welcome Back 🌱</h2>", unsafe_allow_html=True)
    st.info("Your health journey starts here! Stay consistent 💪")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "home"

# -------------------------------
# PAGE NAVIGATION LOGIC
# -------------------------------
if not st.session_state.logged_in:
    # Login/Sign up floating buttons
    st.markdown("""
        <div class='login-buttons'>
            <button onclick="window.location.href='?signup'">Sign Up</button>
            <button onclick="window.location.href='?login'">Login</button>
        </div>
    """, unsafe_allow_html=True)

    # Replace the JavaScript navigation with Streamlit logic
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign Up"):
            st.session_state.page = "signup"
    with col2:
        if st.button("Login"):
            st.session_state.page = "login"

    if st.session_state.page == "home":
        home_page()
    elif st.session_state.page == "signup":
        signup_page()
    elif st.session_state.page == "login":
        login_page()
else:
    dashboard_page()
