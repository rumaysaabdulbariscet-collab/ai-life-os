import streamlit as st
import matplotlib.pyplot as plt
from datetime import date
from streamlit_calendar import calendar
import json, os
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv(dotenv_path=".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("API key not found. Check .env file.")
    st.stop()

client = Groq(api_key=api_key)
# ---------- FILE STORAGE ----------
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# ---------- SAVE CURRENT USER ----------
def save_current_user():
    user = st.session_state.user

    st.session_state.users[user]["tasks"] = st.session_state.tasks
    st.session_state.users[user]["projects"] = st.session_state.projects
    st.session_state.users[user]["calendar_tasks"] = st.session_state.calendar_tasks
    st.session_state.users[user]["points"] = st.session_state.points
    st.session_state.users[user]["deadline_status"] = st.session_state.deadline_status
    st.session_state.users[user]["project_status"] = st.session_state.project_status

    # ✅ ADD THESE
    st.session_state.users[user]["chat"] = st.session_state.chat
    st.session_state.users[user]["history"] = st.session_state.history

    save_users(st.session_state.users)

# ---------- PAGE ----------
st.set_page_config(page_title="AI Life OS", layout="wide")

# ---------- SESSION ----------
def init_state():
    defaults = {
        "users": load_users(),
        "logged_in": False,
        "user": "",
        "tasks": [],
        "calendar_tasks": {},
        "points": 0,
        "deadline_status": {},
        "projects": [],
        "project_status": {},
        "chat": [],        # ✅ ADD
        "history": []      # ✅ ADD
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ---------- LOGIN ----------
if not st.session_state.logged_in:
    st.title("🔐 Login / Signup")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # ---------- LOGIN TAB ----------
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if (
                email in st.session_state.users and
                st.session_state.users[email]["password"] == password
            ):
                st.session_state.logged_in = True
                st.session_state.user = email

                user_data = st.session_state.users[email]

                # LOAD ALL DATA
                st.session_state.tasks = user_data.get("tasks", [])
                st.session_state.projects = user_data.get("projects", [])
                st.session_state.calendar_tasks = user_data.get("calendar_tasks", {})
                st.session_state.points = user_data.get("points", 0)
                st.session_state.deadline_status = user_data.get("deadline_status", {})
                st.session_state.project_status = user_data.get("project_status", {})

                # ✅ LOAD CHAT
                st.session_state.chat = user_data.get("chat", [])
                st.session_state.history = user_data.get("history", [])

                st.rerun()
            else:
                st.error("Invalid credentials")

    # ---------- SIGNUP TAB ----------
    with tab2:
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            st.session_state.users[new_email] = {
                "password": new_password,
                "tasks": [],
                "projects": [],
                "calendar_tasks": {},
                "points": 0,
                "deadline_status": {},
                "project_status": {},
                "chat": [],
                "history": []
            }

            save_users(st.session_state.users)
            st.success("Account created!")

    st.stop()
# ---------- STYLE ----------
st.markdown("""
<style>
.stApp { background-color: #f5f3ff; }
[data-testid="stSidebar"] { background-color: #ede9fe; }

.card {
    background: linear-gradient(135deg, #ffffff, #f3f0ff);
    padding:20px;
    border-radius:16px;
    box-shadow:0 6px 16px rgba(0,0,0,0.08);
    margin-bottom:15px;
    border-left: 6px solid #7c3aed;
}

.task-box {
    background:#ede9fe;
    padding:14px;
    border-radius:10px;
    margin-bottom:12px;
    font-size:16px;
}

.points-text {
    font-size:20px;
    font-weight:600;
    color:#7c3aed;
}
</style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.title("🧠 AI Life OS")
st.sidebar.markdown(f"👤 **{st.session_state.user}**")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Planner", "Projects", "Deadlines", "Performance", "Points", "AI Assistant"]
)
# ---------- DASHBOARD ----------
if page == "Dashboard":
    st.title("📊 Dashboard")

    all_tasks = []

    for t in st.session_state.tasks:
        all_tasks.append({"name": t["name"], "done": t["done"], "type": "planner"})

    for d, tasks in st.session_state.calendar_tasks.items():
        for t in tasks:
            key = f"{d}_{t}"
            all_tasks.append({
                "name": f"{t} ({d})",
                "done": st.session_state.deadline_status.get(key, False),
                "type": "deadline"
            })

    for p in st.session_state.projects:
        all_tasks.append({
            "name": p,
            "done": st.session_state.project_status.get(p, False),
            "type": "project"
        })

    total = len(all_tasks)
    done = sum(1 for t in all_tasks if t["done"])
    pending = total - done
    percent = int((done / total) * 100) if total > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="card"><h4>Total</h4><h2>{total}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="card"><h4>Done</h4><h2>{done}</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="card"><h4>Pending</h4><h2>{pending}</h2></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="card"><h4>Progress</h4><h2>{percent}%</h2></div>', unsafe_allow_html=True)

    left, right = st.columns([2,1])

    with left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        if total > 0:
            col1, col2 = st.columns(2)

            fig1, ax1 = plt.subplots(figsize=(1.8,1.8))
            ax1.pie([done, pending], colors=["#7c3aed","#c4b5fd"], autopct="%1.0f%%")
            ax1.set_aspect('equal')
            col1.pyplot(fig1)

            fig2, ax2 = plt.subplots(figsize=(2.3,2))
            ax2.bar(["Done","Pending"], [done,pending],
                    color=["#7c3aed","#f59e0b"], width=0.4)
            ax2.spines["top"].set_visible(False)
            ax2.spines["right"].set_visible(False)
            col2.pyplot(fig2)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.subheader("📋 All Tasks")

        if total > 0:
            st.progress(percent/100)

        for t in all_tasks:
            tag = "🟣" if t["type"]=="planner" else "🟠" if t["type"]=="deadline" else "🔵"

            if t["done"]:
                st.markdown(
                    f'<div class="task-box">✅ {tag} <span style="text-decoration:line-through;">{t["name"]}</span></div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="task-box">🔲 {tag} {t["name"]}</div>',
                    unsafe_allow_html=True
                )

        st.markdown("---")
        st.subheader("📅 Calendar")

        events = []
        for d, tasks in st.session_state.calendar_tasks.items():
            for t in tasks:
                events.append({"title": t, "start": d})

        calendar(events=events, options={"initialView":"dayGridMonth","height":350})

# ---------- PLANNER ----------
elif page == "Planner":
    st.title("📝 Planner")

    task = st.text_input("Task")

    if st.button("Add") and task:
        st.session_state.tasks.append({"name":task,"done":False})
        save_current_user()
        st.rerun()

    for i,t in enumerate(st.session_state.tasks):
        col1,col2,col3 = st.columns([4,1,1])
        col1.write(t["name"])

        new_val = col2.checkbox("", value=t["done"], key=i)
        st.session_state.tasks[i]["done"] = new_val
        save_current_user()

        if col3.button("❌", key=f"d{i}"):
            st.session_state.tasks.pop(i)
            save_current_user()
            st.rerun()

# ---------- PROJECTS ----------
elif page == "Projects":
    st.title("📂 Projects")

    proj = st.text_input("Project Name")
    deadline = st.date_input("Project Deadline")

    if st.button("Add Project") and proj:
        st.session_state.projects.append(proj)

        d = str(deadline)
        if d not in st.session_state.calendar_tasks:
            st.session_state.calendar_tasks[d] = []

        st.session_state.calendar_tasks[d].append(f"Project: {proj}")

        save_current_user()
        st.rerun()

    st.markdown("---")

    for i, p in enumerate(st.session_state.projects):
        if p not in st.session_state.project_status:
            st.session_state.project_status[p] = False

        col1, col2, col3 = st.columns([4,1,1])

        if st.session_state.project_status[p]:
            col1.markdown(f'<div class="task-box">✅ <s>{p}</s></div>', unsafe_allow_html=True)
        else:
            col1.markdown(f'<div class="task-box">📁 {p}</div>', unsafe_allow_html=True)

        new_val = col2.checkbox("", value=st.session_state.project_status[p], key=f"proj_{i}")

        if new_val and not st.session_state.project_status[p]:
            st.session_state.points += 15
        if not new_val and st.session_state.project_status[p]:
            st.session_state.points -= 15

        st.session_state.project_status[p] = new_val
        save_current_user()

        if col3.button("❌", key=f"del_proj_{i}"):
            st.session_state.projects.pop(i)
            save_current_user()
            st.rerun()

# ---------- DEADLINES ----------
elif page == "Deadlines":
    st.title("⏰ Deadlines")

    selected_date = st.date_input("Select Date")
    key = str(selected_date)

    if key not in st.session_state.calendar_tasks:
        st.session_state.calendar_tasks[key] = []

    task = st.text_input("Task Name")

    if st.button("Add Task") and task:
        st.session_state.calendar_tasks[key].append(task)
        save_current_user()
        st.rerun()

    st.markdown("---")

    for d, tasks in st.session_state.calendar_tasks.items():
        for t in tasks:
            task_key = f"{d}_{t}"

            if task_key not in st.session_state.deadline_status:
                st.session_state.deadline_status[task_key] = False

            col1, col2 = st.columns([4,1])

            if st.session_state.deadline_status[task_key]:
                col1.markdown(
                    f'<div class="task-box">✅ <span style="text-decoration:line-through;">{t} ({d})</span></div>',
                    unsafe_allow_html=True
                )
            else:
                col1.markdown(
                    f'<div class="task-box">📅 {t} ({d})</div>',
                    unsafe_allow_html=True
                )

            new_val = col2.checkbox("", value=st.session_state.deadline_status[task_key], key=task_key)

            if new_val and not st.session_state.deadline_status[task_key]:
                st.session_state.points += 10
            if not new_val and st.session_state.deadline_status[task_key]:
                st.session_state.points -= 10

            st.session_state.deadline_status[task_key] = new_val
            save_current_user()

# ---------- AI ASSISTANT ----------
elif page == "AI Assistant":
    st.title("🤖 AI Assistant")

    # ---------- SESSION ----------
    if "chat" not in st.session_state:
        st.session_state.chat = []

    if "history" not in st.session_state:
        st.session_state.history = []

    # ---------- LAYOUT ----------
    left, right = st.columns([3,1])

    # ---------- INPUT ----------
    with left:
        user_input = st.text_input("Ask anything...")

        if st.button("Send") and user_input:

            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a helpful study assistant."},
                        {"role": "user", "content": user_input}
                    ]
                )

                reply = response.choices[0].message.content

            except Exception as e:
                reply = f"❌ {str(e)}"

            # store chat (for UI)
            st.session_state.chat.append({"role": "user", "text": user_input})
            st.session_state.chat.append({"role": "ai", "text": reply})

            # store history (for right panel)
            st.session_state.history.append({
                "question": user_input,
                "answer": reply
            })
            save_current_user()

    # ---------- CHAT DISPLAY ----------
    with left:
        for msg in st.session_state.chat:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="text-align:right;
                background:#7c3aed;
                color:white;
                padding:10px;
                border-radius:12px;
                margin-bottom:8px">
                {msg["text"]}
                </div>
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                <div style="text-align:left;
                background:#ede9fe;
                padding:10px;
                border-radius:12px;
                margin-bottom:8px">
                {msg["text"]}
                </div>
                """, unsafe_allow_html=True)

        # ---------- RIGHT PANEL ----------
    with right:
        st.subheader("🕘 Recent")

        for i, item in enumerate(reversed(st.session_state.history)):
            if st.button(item["question"][:25], key=f"hist_{i}"):

                st.session_state.chat = [
                    {"role": "user", "text": item["question"]},
                    {"role": "ai", "text": item["answer"]}
                ]

                save_current_user()
                st.rerun()
# ---------- PERFORMANCE ----------
elif page == "Performance":
    st.title("📈 Performance")

    total = len(st.session_state.tasks)
    done = sum(1 for t in st.session_state.tasks if t["done"])

    if total > 0:
        percent = int((done/total)*100)

        st.write(f"Score: {percent}%")
        st.progress(percent/100)

        fig, ax = plt.subplots(figsize=(2.2,1.3))

        ax.plot(["Start","Now"], [0, percent], marker='o', color="#7c3aed")
        ax.set_ylim(0,100)
        ax.set_title("Progress Trend", fontsize=9)
        ax.tick_params(labelsize=7)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.pyplot(fig, use_container_width=False)

# ---------- POINTS ----------
elif page == "Points":
    st.title("🏆 Points")
    st.markdown(f'<div class="points-text">Total Points: {st.session_state.points}</div>', unsafe_allow_html=True)