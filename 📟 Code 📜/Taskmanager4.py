import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import hashlib

# --- App Config ---
st.set_page_config(page_title="AI 🤖 Task 📜 Manager ❤️‍🔥", page_icon="🤖", layout="wide")

# =========================
# 🔐 DATABASE
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

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def create_user(u, p):
    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (u, hash_password(p)))
        conn.commit()
        return True
    except:
        return False

def login_user(u, p):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_password(p)))
    return c.fetchone()

# =========================
# SESSION
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=["Task", "Priority", "Due Date", "Completed"])

# =========================
# LOGIN / SIGNUP
# =========================
if not st.session_state.logged_in:

    st.markdown("<h2 style='text-align:center;color:#C2FC00;'>AI 🤖 Task Manager</h2>", unsafe_allow_html=True)

    menu = st.radio("Select", ["Login 🔐", "Signup 🆕"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if menu == "Signup 🆕":
        if st.button("Create Account"):
            if create_user(username, password):
                st.success("Account created!")
            else:
                st.error("User exists")

    else:
        if st.button("Login ➡️"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid login")

    st.stop()

# =========================
# 🌙 THEME TOGGLE
# =========================
theme = st.toggle("🌙 Dark Mode", value=True)

if theme:
    bg_color = "#0e1117"
    card_bg = "rgba(255,255,255,0.05)"
    text_color = "white"
else:
    bg_color = "#f5f5f5"
    card_bg = "rgba(0,0,0,0.05)"
    text_color = "black"

# =========================
# 🌠 PARTICLES + STYLE
# =========================
st.markdown(f"""
<style>
body {{
    background-color: {bg_color};
}}

#particles-js {{
    position: fixed;
    width: 100%;
    height: 100%;
    z-index: -1;
}}

.glass-card {{
    background: {card_bg};
    backdrop-filter: blur(12px);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 12px;
    border: 1px solid rgba(255,255,255,0.1);
    color: {text_color};
    transition: 0.3s;
}}

.glass-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    border: 1px solid #C2FC00;
}}
</style>

<div id="particles-js"></div>

<script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
<script>
particlesJS("particles-js", {{
  "particles": {{
    "number": {{ "value": 60 }},
    "color": {{ "value": "#C2FC00" }},
    "shape": {{ "type": "circle" }},
    "opacity": {{ "value": 0.5 }},
    "size": {{ "value": 3 }},
    "line_linked": {{
      "enable": true,
      "distance": 150,
      "color": "#C2FC00",
      "opacity": 0.2
    }},
    "move": {{ "enable": true, "speed": 2 }}
  }},
  "interactivity": {{
    "events": {{
      "onhover": {{ "enable": true, "mode": "repulse" }}
    }}
  }}
}});
</script>
""", unsafe_allow_html=True)

# =========================
# MAIN APP
# =========================
st.markdown(f"<h1 style='text-align:center;color:#C2FC00;'>Welcome {st.session_state.username} 🚀</h1>", unsafe_allow_html=True)

if st.sidebar.button("Logout ➡️"):
    st.session_state.logged_in = False
    st.rerun()

# =========================
# ADD TASK
# =========================
st.sidebar.header("Add Task")

task = st.sidebar.text_input("Task")
priority = st.sidebar.selectbox("Priority", ["High 🔥", "Medium 🤔", "Low 📉"])
due = st.sidebar.date_input("Due Date", datetime.today())

if st.sidebar.button("Add ➕"):
    if task:
        st.session_state.tasks = pd.concat([
            st.session_state.tasks,
            pd.DataFrame([{
                "Task": task,
                "Priority": priority,
                "Due Date": due,
                "Completed": False
            }])
        ], ignore_index=True)

# =========================
# CARD UI
# =========================
def task_card(task, priority, due, completed):
    color = "#FF4B4B" if "High" in priority else "#FFA500" if "Medium" in priority else "#4CAF50"
    status = "✅ Completed" if completed else "⏳ Pending"

    return f"""
    <div class="glass-card" style="border-left:5px solid {color}">
        <h4>{task}</h4>
        <p>📅 {due}<br>🔥 {priority}<br>{status}</p>
    </div>
    """

# =========================
# DISPLAY TASKS
# =========================
st.subheader("Your Tasks")

for i, row in st.session_state.tasks.iterrows():
    col1, col2 = st.columns([4,1])

    with col1:
        st.markdown(task_card(row["Task"], row["Priority"], row["Due Date"], row["Completed"]), unsafe_allow_html=True)

    with col2:
        if st.button("✔️", key=f"done{i}"):
            st.session_state.tasks.at[i, "Completed"] = True

        if st.button("🗑️", key=f"del{i}"):
            st.session_state.tasks = st.session_state.tasks.drop(i)
            st.rerun()

# =========================
# AI SUGGESTIONS
# =========================
st.subheader("AI Suggestions")

today = datetime.today().date()

overdue = st.session_state.tasks[
    (st.session_state.tasks["Due Date"] < today) & (~st.session_state.tasks["Completed"])
]

high = st.session_state.tasks[
    (st.session_state.tasks["Priority"].str.contains("High")) & (~st.session_state.tasks["Completed"])
]

if not overdue.empty:
    st.warning("⚠️ Overdue tasks!")

if not high.empty:
    st.info("🔥 Focus on high priority!")

if overdue.empty and high.empty:
    st.success("✅ All good!")

# =========================
# FOOTER
# =========================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>🚀 AI Task Manager</p>", unsafe_allow_html=True)

# streamlit run Taskmanager4.py

# PS E:\> cd "E:\GitHub Co-Pilot DEV Days\handson-lab"
# PS E:\GitHub Co-Pilot DEV Days\handson-lab> streamlit run Taskmanager4.py