import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
import random

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="NuTraDaily", page_icon="🥬", layout="wide")

# -------------------------------
# 🌈 CUSTOM CSS (Dark sidebar + bright text)
# -------------------------------
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f1faee 0%, #d8f3dc 30%, #b7e4c7 70%, #95d5b2 100%);
    background-attachment: fixed;
    font-family: 'Poppins', sans-serif;
    color: #1b4332;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2d6a4f 0%, #1b4332 100%);
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
[data-testid="stSidebar"] .stRadio div[role='radiogroup'] label {
    color: #fefae0 !important;
    font-weight: 600;
}
[data-testid="stSidebar"] .stRadio div[role='radiogroup'] label:hover {
    color: #b7e4c7 !important;
    text-shadow: 0 0 10px #b7e4c7;
}

/* Buttons */
button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    background-color: #52b788 !important;
    color: white !important;
}
button:hover {
    background-color: #40916c !important;
}

/* Card effect */
.stImage, [data-testid="stDataFrame"], .stPlotlyChart {
    background: rgba(255, 255, 255, 0.85);
    border-radius: 15px;
    padding: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -------------------------------
# HEADER IMAGE
# -------------------------------
st.image(
    "https://images.unsplash.com/photo-1606787366850-de6330128bfc?auto=format&fit=crop&w=1400&q=80",
    use_column_width=True,
)

# -------------------------------
# GREETING + MOTIVATION
# -------------------------------
current_hour = datetime.datetime.now().hour
if current_hour > 12am:
    greeting = "🌞 Good morning!"
elif current_hour > 3pm:
    greeting = "🌤️ Good afternoon!"
else:
    greeting = "🌙 Good evening!"

motivations = [
    "💧 Stay hydrated — your body thanks you for every sip!",
    "🍎 Every healthy choice adds up — keep going!",
    "🏃‍♀️ Don’t stop now! You’re closer than you think!",
    "💚 Your health journey is progress, not perfection.",
    "🌿 Take a deep breath. You’re doing amazing!"
]
st.toast(f"{greeting} {random.choice(motivations)}", icon="💪")

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
st.sidebar.title("🥬 NuTraDaily ")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "🍎 Nutrition & Diet", "💧 Water Tracker", "📸 Food Photo", "🎯 Goal Progress", "📊 Weekly Report", "🔥 Daily Streak 🏅"]
)

# -------------------------------
# FILES
# -------------------------------
data_file = "progress.csv"
streak_file = "streak.csv"

if not os.path.exists(data_file):
    df = pd.DataFrame(columns=["Date", "Calories", "Water(L)", "GoalWeight"])
    df.to_csv(data_file, index=False)
if not os.path.exists(streak_file):
    s_df = pd.DataFrame(columns=["Date"])
    s_df.to_csv(streak_file, index=False)

# -------------------------------
# PAGES
# -------------------------------
if page == "🏠 Home":
    st.title("💧 Welcome to NuTraDaily 🌿")
    st.subheader("Your All-in-One Wellness Dashboard")
    st.image(
        "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=1000&q=80",
        caption="Eat Well • Drink Well • Live Well",
        use_column_width=True,
    )
    st.success("💡 Use the sidebar to explore each section!")

# -------------------------------
# 🍎 NUTRITION & DIET PAGE
# -------------------------------
elif page == "🍎 Nutrition & Diet":
    st.title("🍎 Nutrition & Diet Plan")

    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 10, 100, 20)
        gender = st.selectbox("Gender", ["Male", "Female"])
        height = st.number_input("Height (cm)", 100, 250, 170)
    with col2:
        weight = st.number_input("Weight (kg)", 30, 200, 65)
        activity = st.selectbox("Activity Level", ["Low", "Moderate", "High"])

    # Calorie calculation
    if gender == "Male":
        bmr = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age)
    else:
        bmr = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age)
    activity_factor = {"Low": 1.2, "Moderate": 1.55, "High": 1.9}[activity]
    daily_calories = round(bmr * activity_factor)
    st.success(f"Estimated daily calorie need: **{daily_calories} kcal/day**")

    # Suggested meals
    st.markdown("### 🍽️ Suggested Meal Plan")
    meals = {
        "Breakfast": ["Oats with banana", "Egg sandwich", "Avocado toast", "Smoothie bowl"],
        "Lunch": ["Dal + roti + salad", "Grilled chicken + rice", "Paneer wrap", "Veg bowl"],
        "Dinner": ["Veg soup + bread", "Tofu stir fry", "Khichdi + curd", "Grilled veggies"]
    }

    col3, col4, col5 = st.columns(3)
    with col3:
        breakfast = st.selectbox("Breakfast", meals["Breakfast"])
    with col4:
        lunch = st.selectbox("Lunch", meals["Lunch"])
    with col5:
        dinner = st.selectbox("Dinner", meals["Dinner"])

    st.info(f"✅ Your Today's Plan:\n- 🥣 {breakfast}\n- 🍛 {lunch}\n- 🍲 {dinner}")

    # Nutrition chart
    st.markdown("### 📊 Nutrition Breakdown")
    labels = ["Carbohydrates", "Protein", "Fats"]
    sizes = [50, 30, 20]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    # Daily nutrition tip
    tips = [
        "🥦 Add more greens to your lunch today!",
        "🍊 Start your morning with a vitamin C boost!",
        "🍓 Eat colorful — the more colors, the more nutrients!",
        "🥑 Healthy fats keep your heart happy 💚",
        "🌾 Include whole grains to stay full longer!"
    ]
    st.success(random.choice(tips))

# -------------------------------
# 💧 WATER TRACKER
# -------------------------------
elif page == "💧 Water Tracker":
    st.title("💧 Water Tracker")
    weight = st.number_input("Your Weight (kg)", 30, 200, 65)
    water_goal = weight * 35 / 1000
    intake = st.slider("Water consumed today (litres)", 0.0, 5.0, 1.0, 0.1)
    progress = min(intake / water_goal, 1.0)
    st.progress(progress)
    st.write(f"You drank **{intake:.1f} L** out of **{water_goal:.1f} L** goal 💧")

# -------------------------------
# 📸 FOOD PHOTO
# -------------------------------
elif page == "📸 Food Photo":
    st.title("📸 Upload Your Meal")
    uploaded_file = st.file_uploader("Upload your food photo", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Your Meal 📷", use_column_width=True)

# -------------------------------
# 🎯 GOAL PROGRESS
# -------------------------------
elif page == "🎯 Goal Progress":
    st.title("🎯 Goal Progress")
    current = st.number_input("Current weight (kg)", 30, 200, 70)
    goal = st.number_input("Goal weight (kg)", 30, 200, 60)
    weekly_loss = st.slider("Expected weekly change (kg)", 0.1, 2.0, 0.5)
    diff = abs(current - goal)
    weeks_needed = diff / weekly_loss
    st.info(f"Estimated time to reach goal: **{weeks_needed:.1f} weeks**")

# -------------------------------
# 📊 WEEKLY REPORT
# -------------------------------
elif page == "📊 Weekly Report":
    st.title("📊 Weekly Report")
    df = pd.read_csv(data_file)
    if df.empty:
        st.warning("No data yet!")
    else:
        df["Date"] = pd.to_datetime(df["Date"])
        st.dataframe(df.tail(7))

# -------------------------------
# 🔥 DAILY STREAK + ACHIEVEMENTS
# -------------------------------
elif page == "🔥 Daily Streak 🏅":
    st.title("🔥 Daily Streak Tracker + Achievements 🏅")
    s_df = pd.read_csv(streak_file)
    today = datetime.date.today()

    if st.button("✅ Mark Today as Done"):
        if str(today) not in s_df["Date"].values:
            s_df = pd.concat([s_df, pd.DataFrame({"Date": [today]})], ignore_index=True)
            s_df.to_csv(streak_file, index=False)
            st.success("🔥 Day marked! You’re on fire!")
        else:
            st.info("✅ You already marked today, champ!")

    if not s_df.empty:
        s_df["Date"] = pd.to_datetime(s_df["Date"])
        s_df = s_df.sort_values("Date")
        current_streak = best_streak = 1

        for i in range(1, len(s_df)):
            if (s_df["Date"].iloc[i] - s_df["Date"].iloc[i - 1]).days == 1:
                current_streak += 1
                best_streak = max(best_streak, current_streak)
            else:
                current_streak = 1

        st.subheader(f"🔥 Current Streak: {current_streak} days")
        st.subheader(f"🏆 Best Streak: {best_streak} days")

        st.markdown("---")
        st.markdown("### 🏅 Your Achievements")

        if best_streak < 3:
            st.info("🎖️ **Newbie Starter** — You’ve begun your health journey!")
            st.image("https://cdn-icons-png.flaticon.com/512/616/616408.png", width=100)
        elif best_streak < 7:
            st.success("🌿 **Consistency Champ** — You’ve maintained 3+ days of streak!")
            st.image("https://cdn-icons-png.flaticon.com/512/1077/1077086.png", width=100)
        elif best_streak < 14:
            st.success("💪 **Health Hero** — You’ve gone beyond a week of dedication!")
            st.image("https://cdn-icons-png.flaticon.com/512/3176/3176364.png", width=100)
        elif best_streak >= 14:
            st.balloons()
            st.success("🔥 **Wellness Warrior!** — Two weeks+ of pure discipline!")
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)

    else:
        st.warning("No streaks yet — click ‘Mark Today as Done’ to begin!")

# -------------------------------
# FOOTER
# -------------------------------
st.sidebar.markdown("---")
st.sidebar.info("🌿 Made with 💚 by You — NuTraDaily 💧")



