import streamlit as st
import pandas as pd
from datetime import datetime
import random
import sqlite3
import hashlib

# --- App Configuration ---
st.set_page_config(
    page_title="AI 🤖 Task 📜 Manager ❤️‍🔥",
    page_icon="🤖",
    layout="wide"
)

# =========================
# 🔐 DATABASE SETUP
# =========================
def connect_db():
    return sqlite3.connect("users.db", check_same_thread=False)

conn = connect_db()
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")
conn.commit()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone()

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=["Task", "Priority", "Due Date", "Completed"])

# =========================
# 🔐 LOGIN / SIGNUP UI
# =========================
if not st.session_state.logged_in:

    st.markdown("<h2 style='text-align:center;color:#C2FC00;'>AI 🤖 Task Manager</h2>", unsafe_allow_html=True)

    menu = st.radio("Select Option", ["Login 🔐", "Signup 🆕"])

    username = st.text_input("Username 👨‍💻")
    password = st.text_input("Password 🔐", type="password")

    if menu == "Signup 🆕":
        if st.button("Create Account 🪄"):
            if create_user(username, password):
                st.success("✅ Account created! Please login.")
            else:
                st.error("⚠️ Username already exists")

    else:
        if st.button("Login ➡️"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome {username} 🎉")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

    st.stop()

# =========================
# MAIN APP
# =========================
st.markdown(f"<h1 style='text-align:center;color:#C2FC00;'>Welcome, {st.session_state.username}! 🎉</h1>", unsafe_allow_html=True)

# Logout
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# =========================
# ADD TASK
# =========================
st.sidebar.header("📝 Add Task")

task_name = st.sidebar.text_input("Task Name")
priority = st.sidebar.selectbox("Priority", ["High 🔥", "Medium 🤔", "Low 📉"])
due_date = st.sidebar.date_input("Due Date", datetime.today())

if st.sidebar.button("Add Task"):
    if task_name.strip() == "":
        st.sidebar.error("Task cannot be empty")
    elif task_name in st.session_state.tasks["Task"].values:
        st.sidebar.warning("Task already exists")
    else:
        new_task = {
            "Task": task_name,
            "Priority": priority,
            "Due Date": due_date,
            "Completed": False
        }
        st.session_state.tasks = pd.concat(
            [st.session_state.tasks, pd.DataFrame([new_task])],
            ignore_index=True
        )
        st.sidebar.success("Task added!")

# =========================
# SORT TASKS
# =========================
if not st.session_state.tasks.empty:
    priority_order = {"High 🔥": 1, "Medium 🤔": 2, "Low 📉": 3}
    st.session_state.tasks["PriorityOrder"] = st.session_state.tasks["Priority"].map(priority_order)

    st.session_state.tasks = st.session_state.tasks.sort_values(
        by=["PriorityOrder", "Due Date"]
    ).drop(columns=["PriorityOrder"])

# =========================
# 📱 CARD UI
# =========================
def task_card(task, priority, due, completed):
    color = "#FF4B4B" if priority.startswith("High") else "#FFA500" if priority.startswith("Medium") else "#4CAF50"
    status = "✅ Completed" if completed else "⏳ Pending"

    return f"""
    <div style="
        background-color:#1e1e1e;
        padding:15px;
        border-radius:12px;
        margin-bottom:10px;
        border-left:6px solid {color};
    ">
        <h4 style="color:white;">{task}</h4>
        <p style="color:lightgray;">
        📅 {due} <br>
        🔥 {priority} <br>
        {status}
        </p>
    </div>
    """

# =========================
# DISPLAY TASKS
# =========================
st.subheader("📋 Your Tasks")

if st.session_state.tasks.empty:
    st.info("No tasks yet")
else:
    for i, row in st.session_state.tasks.iterrows():
        col1, col2 = st.columns([4,1])

        with col1:
            st.markdown(task_card(row["Task"], row["Priority"], row["Due Date"], row["Completed"]), unsafe_allow_html=True)

        with col2:
            if st.button("✔️", key=f"done_{i}"):
                st.session_state.tasks.at[i, "Completed"] = True

            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.tasks = st.session_state.tasks.drop(i)
                st.rerun()

# =========================
# 🤖 AI SUGGESTIONS
# =========================
st.subheader("AI 🤖 Suggestions")

if not st.session_state.tasks.empty:
    today = datetime.today().date()

    overdue = st.session_state.tasks[
        (st.session_state.tasks["Due Date"] < today) & (~st.session_state.tasks["Completed"])
    ]

    high = st.session_state.tasks[
        (st.session_state.tasks["Priority"].str.startswith("High")) & (~st.session_state.tasks["Completed"])
    ]

    if not overdue.empty:
        st.warning("⚠️ You have overdue tasks. Complete them ASAP!")

    if not high.empty:
        st.info("🔥 Focus on high priority tasks first!")

    if overdue.empty and high.empty:
        st.success("✅ Everything is on track!")

# =========================
# FOOTER
# =========================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#FC6100;'>AI 🤖 Task Manager</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#C2FC00;'>Developed by Hemant ❤️‍🔥</p>", unsafe_allow_html=True)

# streamlit run Taskmanager3.py