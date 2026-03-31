import streamlit as st
import pandas as pd
from datetime import datetime

# --- App Configuration ---
st.set_page_config(
    page_title="AI 🤖 Task 📜 Manager ❤️‍🔥",
    page_icon="🤖",
    layout="wide"
)

# --- Title ---
st.markdown(
    "<h1 style='text-align: center; color: #C2FC00;'>AI 🤖 Task 📜 Manager ❤️‍🔥</h1>",
    unsafe_allow_html=True
)

# --- Initialize session state ---
if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=["Task", "Priority", "Due Date", "Completed"])

# --- Sidebar for Adding Tasks ---
st.sidebar.header("📝 Add New Task 📜")
task_name = st.sidebar.text_input("Task 📜 Name")
priority = st.sidebar.selectbox("Priority 📈", ["High 🔥", "Medium 🤔", "Low 📉"])
due_date = st.sidebar.date_input("Due Date 📅", datetime.today())

if st.sidebar.button("📝 Add Task 📜"):
    if task_name.strip() != "":
        new_task = {
            "Task": task_name.strip(),
            "Priority": priority,
            "Due Date": due_date,
            "Completed": False
        }
        st.session_state.tasks = pd.concat(
            [st.session_state.tasks, pd.DataFrame([new_task])],
            ignore_index=True
        )
        st.sidebar.success(f"Task '{task_name}' added!")
    else:
        st.sidebar.error("💀 Task name cannot be empty! ☠️")

# --- Ensure Completed column is boolean ---
if not st.session_state.tasks.empty:
    st.session_state.tasks["Completed"] = st.session_state.tasks["Completed"].fillna(False).astype(bool)

# --- Sort Tasks by Priority and Due Date ---
if not st.session_state.tasks.empty:
    priority_order = {"High 🔥": 1, "Medium 🤔": 2, "Low 📉": 3}
    st.session_state.tasks["PriorityOrder"] = st.session_state.tasks["Priority"].map(priority_order)
    st.session_state.tasks = st.session_state.tasks.sort_values(
        by=["PriorityOrder", "Due Date"], ascending=[True, True]
    ).drop(columns=["PriorityOrder"])

# --- Task Table with Checkbox for Completed ---
st.subheader("Task List 📋")

if st.session_state.tasks.empty:
    st.info("No tasks yet. Add some tasks using the sidebar 📝.")
else:
    # Function to color-code and highlight
    def style_tasks(row):
        styles = []
        for col in row.index:
            style = ""
            if col == "Task" and row.Completed:
                style += "text-decoration: line-through; color: grey;"
            if col == "Priority":
                if row.Priority.startswith("High"):
                    style += "color: red; font-weight: bold;"
                elif row.Priority.startswith("Medium"):
                    style += "color: orange;"
                elif row.Priority.startswith("Low"):
                    style += "color: green;"
            if col == "Due Date" and row["Due Date"] <= pd.Timestamp.today() and not row.Completed:
                style += "background-color: #FFFACD;"  # highlight upcoming tasks
            styles.append(style)
        return styles

    # Use experimental_data_editor for interactive checkboxes
    edited_tasks = st.data_editor(
        st.session_state.tasks,
        num_rows="dynamic",
        use_container_width=True
    )
    st.session_state.tasks = edited_tasks

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
    high_priority_tasks = st.session_state.tasks[
        (st.session_state.tasks["Priority"].str.startswith("High")) & (~st.session_state.tasks["Completed"])
    ]
    upcoming_tasks = st.session_state.tasks[
        (st.session_state.tasks["Due Date"] <= pd.Timestamp.today()) & (~st.session_state.tasks["Completed"])
    ]
    
    st.markdown("### Recommended Actions 💯")
    if not high_priority_tasks.empty:
        st.markdown(f"- 🔥 Focus on high-priority tasks: {', '.join(high_priority_tasks['Task'].tolist())}")
    if not upcoming_tasks.empty:
        st.markdown(f"- ⏰ Tasks due soon: {', '.join(upcoming_tasks['Task'].tolist())}")
    if high_priority_tasks.empty and upcoming_tasks.empty:
        st.markdown("- ✅ All tasks are on track!")

# --- Centered Captions ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FC6100;'>AI 🤖 Task 📜 Manager ❤️‍🔥</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #C2FC00;'>Designed & Developed</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FCCE00;'>Hemant Katta ❤️‍🔥</p>", unsafe_allow_html=True)