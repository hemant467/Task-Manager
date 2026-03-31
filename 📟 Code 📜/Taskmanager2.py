import streamlit as st
import pandas as pd
from datetime import datetime
import random

# --- App Configuration ---
st.set_page_config(
    page_title="AI 🤖 Task 📜 Manager ❤️‍🔥",
    page_icon="🤖",
    layout="wide"
)

# --- User database (demo) ---
USER_CREDENTIALS = {
    "hemant": "password123",
    "admin": "admin123"
}

# --- Initialize session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "captcha" not in st.session_state:
    st.session_state.captcha = None
if "captcha_answer" not in st.session_state:
    st.session_state.captcha_answer = None
if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=["Task", "Priority", "Due Date", "Completed"])

# --- Generate math CAPTCHA ---
def generate_captcha():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    st.session_state.captcha = f"{a} + {b} = ?"
    st.session_state.captcha_answer = str(a + b)

# --- Login Page ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #C2FC00;'>Login to AI 🤖 Task Manager</h2>", unsafe_allow_html=True)
    
    username = st.text_input("Username 👨‍💻")
    password = st.text_input("Password 🔐", type="password")

    if st.session_state.captcha is None:
        generate_captcha()
    captcha_input = st.text_input(f"CAPTCHA: {st.session_state.captcha}")

    login_btn = st.button("Login ➡️")

    if login_btn:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            if captcha_input.strip() == st.session_state.captcha_answer:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
            else:
                st.error("💀 ❌ CAPTCHA is incorrect ☠️. Try again.")
                generate_captcha()  # regenerate CAPTCHA
        else:
            st.error("💀 ❌ Invalid username or password ☠️")
            generate_captcha()  # regenerate CAPTCHA
    st.stop()  # Stop execution until login

# --- Welcome Message ---
st.markdown(f"<h1 style='text-align: center; color: #C2FC00;'>Welcome, {st.session_state.username}! 🎉</h1>", unsafe_allow_html=True)

# --- Logout Button ---
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.captcha = None
    st.session_state.captcha_answer = None
    st.experimental_rerun()

# --- Sidebar: Add Task ---
st.sidebar.header("📝 Add New Task 📜")
task_name = st.sidebar.text_input("Task 📜 Name")
priority = st.sidebar.selectbox("Priority 📈", ["High 🔥", "Medium 🤔", "Low 📉"])
due_date = st.sidebar.date_input("Due Date 📅", datetime.today())

if st.sidebar.button("📝 Add Task 📜"):
    if task_name.strip() != "":
        new_task = {
            "Task": task_name.strip(),
            "Priority": priority,
            "Due Date": due_date,  # keep as date
            "Completed": False
        }
        st.session_state.tasks = pd.concat(
            [st.session_state.tasks, pd.DataFrame([new_task])],
            ignore_index=True
        )
        st.sidebar.success(f"Task '{task_name}' added!")
    else:
        st.sidebar.error("💀 Task name cannot be empty! ☠️")

# --- Ensure proper types ---
if not st.session_state.tasks.empty:
    st.session_state.tasks["Due Date"] = pd.to_datetime(st.session_state.tasks["Due Date"]).dt.date
    st.session_state.tasks["Completed"] = st.session_state.tasks["Completed"].fillna(False).astype(bool)

# --- Sort Tasks by Priority and Due Date ---
if not st.session_state.tasks.empty:
    priority_order = {"High 🔥": 1, "Medium 🤔": 2, "Low 📉": 3}
    st.session_state.tasks["PriorityOrder"] = st.session_state.tasks["Priority"].map(priority_order)
    st.session_state.tasks = st.session_state.tasks.sort_values(
        by=["PriorityOrder", "Due Date"], ascending=[True, True]
    ).drop(columns=["PriorityOrder"])

# --- Task Table with Styling ---
st.subheader("Task List 📋")
if st.session_state.tasks.empty:
    st.info("No tasks yet. Add some tasks using the sidebar 📝.")
else:
    today = datetime.today().date()  # date-only for comparison

    def highlight_overdue(row):
        if not row["Completed"] and row["Due Date"] < today:
            return ["background-color: #FFCCCC"]*len(row)
        return [""]*len(row)

    st.dataframe(
        st.session_state.tasks.style.apply(highlight_overdue, axis=1),
        use_container_width=True
    )

# --- Delete Task ---
st.subheader("Manage Tasks 🗑️")
if not st.session_state.tasks.empty:
    task_to_delete = st.selectbox("Delete ❌ Task", st.session_state.tasks["Task"].tolist())
    if st.button("Delete 🗑️ Task"):
        st.session_state.tasks = st.session_state.tasks[
            st.session_state.tasks["Task"] != task_to_delete
        ]
        st.warning(f"Task '{task_to_delete}' deleted!")

# --- AI Suggestions ---
st.subheader("AI 🤖 Suggestions 📝")
if st.session_state.tasks.empty:
    st.info("Add tasks to get AI suggestions.")
else:
    today = datetime.today().date()

    # High-priority incomplete tasks
    high_priority_tasks = st.session_state.tasks[
        (st.session_state.tasks["Priority"].str.startswith("High")) & (~st.session_state.tasks["Completed"])
    ]

    # Overdue tasks (past due & incomplete)
    overdue_tasks = st.session_state.tasks[
        (st.session_state.tasks["Due Date"] < today) & (~st.session_state.tasks["Completed"])
    ]

    # Upcoming tasks (today or future & incomplete)
    upcoming_tasks = st.session_state.tasks[
        (st.session_state.tasks["Due Date"] >= today) & (~st.session_state.tasks["Completed"])
    ]

    st.markdown("### Recommended Actions 💯")

    if not high_priority_tasks.empty:
        st.markdown(f"- 🔥 **High-priority tasks:** {', '.join(high_priority_tasks['Task'].tolist())}")

    if not overdue_tasks.empty:
        st.markdown(f"- ⚠️ **Overdue tasks:** {', '.join(overdue_tasks['Task'].tolist())}")

    if not upcoming_tasks.empty:
        st.markdown(f"- ⏰ **Upcoming tasks:** {', '.join(upcoming_tasks['Task'].tolist())}")

    if high_priority_tasks.empty and overdue_tasks.empty and upcoming_tasks.empty:
        st.markdown("- ✅ All tasks are on track!")

# --- Centered Captions ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FC6100;'>AI 🤖 Task 📜 Manager ❤️‍🔥</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #C2FC00;'>Designed & Developed by</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FCCE00;'>Hemant Katta ❤️‍🔥</p>", unsafe_allow_html=True)

# streamlit run Taskmanager2.py