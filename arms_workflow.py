import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import time

# ======================================
# ENTERPRISE CONFIGURATION
# ======================================

st.set_page_config(
    page_title="ARMS Workflow Management",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Enterprise Styling
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .enterprise-header {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-bottom: 4px solid #2980b9;
    }
    .metric-card-enterprise {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border: 1px solid #2c3e50;
    }
    .metric-value-enterprise {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0.5rem 0;
    }
    .metric-label-enterprise {
        font-size: 0.9rem;
        color: #ecf0f1;
        font-weight: 600;
        text-transform: uppercase;
    }
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-pending { background: #fff3cd; color: #856404; }
    .status-in-progress { background: #d1ecf1; color: #0c5460; }
    .status-completed { background: #d4edda; color: #155724; }
    .status-under-review { background: #f8d7da; color: #721c24; }
    .priority-high { background: #f8d7da; color: #721c24; }
    .priority-medium { background: #fff3cd; color: #856404; }
    .priority-low { background: #d1ecf1; color: #0c5460; }
</style>
""", unsafe_allow_html=True)

# ======================================
# USER DATABASE (BACKEND)
# ======================================

USERS = {
    "admin": {"password": "admin123", "role": "manager", "name": "System Administrator"},
    "nisarg": {"password": "nisarg123", "role": "analyst", "name": "Nisarg Thakker"},
    "komal": {"password": "komal123", "role": "analyst", "name": "Komal Khamar"},
    "ayushi": {"password": "ayushi123", "role": "analyst", "name": "Ayushi Chandel"},
}

ANALYSTS = ["Nisarg Thakker", "Komal Khamar", "Ayushi Chandel"]

def authenticate(username, password):
    """Backend authentication function"""
    if username in USERS and USERS[username]["password"] == password:
        return USERS[username]
    return None

# ======================================
# SESSION STATE INITIALIZATION (BACKEND)
# ======================================

def initialize_session_state():
    """Initialize all backend state"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
        
    # Task management backend
    if "tasks" not in st.session_state:
        st.session_state.tasks = create_sample_tasks()
    if "next_task_id" not in st.session_state:
        st.session_state.next_task_id = 1280

def create_sample_tasks():
    """Backend: Create sample tasks data"""
    tasks = []
    
    # Sample completed tasks
    sample_data = [
        {"Task_ID": 1270, "Task_Type": "Tier II", "Company_Name": "US Foods Holding Corp.", "Document_Type": "10-Q", "Priority": "High", "Status": "Under Review", "Tier1_Completed_Date_Time": "November 24, 2025 8:44 AM", "Assigned_User": "Ayushi Chandel"},
        {"Task_ID": 1269, "Task_Type": "Tier II", "Company_Name": "Medline Inc - PFE 2022", "Document_Type": "10-K", "Priority": "High", "Status": "Completed", "Tier1_Completed_Date_Time": "November 21, 2025 2:28 PM", "Assigned_User": "Komal Khamar"},
        {"Task_ID": 1268, "Task_Type": "Tier II", "Company_Name": "Medline Inc - 2Q", "Document_Type": "10-Q", "Priority": "High", "Status": "Completed", "Tier1_Completed_Date_Time": "November 21, 2025 2:20 PM", "Assigned_User": "Komal Khamar"},
    ]
    
    # Add pending tasks
    for i in range(10):
        tasks.append({
            "Task_ID": 1250 - i,
            "Task_Type": np.random.choice(["Tier I", "Tier II"]),
            "Company_Name": np.random.choice(["Apple Inc", "Microsoft Corp", "Google LLC", "Amazon Inc", "Tesla Inc"]),
            "Document_Type": np.random.choice(["10-Q", "10-K", "8-K"]),
            "Priority": np.random.choice(["High", "Medium", "Low"]),
            "Status": "Pending",
            "Tier1_Completed_Date_Time": "",
            "Assigned_User": "Unassigned"
        })
    
    tasks.extend(sample_data)
    return tasks

# ======================================
# BACKEND FUNCTIONS
# ======================================

def get_next_task():
    """Backend: Get next available task"""
    available_tasks = [task for task in st.session_state.tasks 
                      if task["Status"] == "Pending" and task["Assigned_User"] == "Unassigned"]
    if available_tasks:
        return available_tasks[0]
    return None

def assign_task_to_user(task_id, user):
    """Backend: Assign task to user"""
    for task in st.session_state.tasks:
        if task["Task_ID"] == task_id:
            task["Assigned_User"] = user
            task["Status"] = "In Progress"
            return True
    return False

def update_task_status(task_id, new_status):
    """Backend: Update task status"""
    for task in st.session_state.tasks:
        if task["Task_ID"] == task_id:
            task["Status"] = new_status
            if new_status == "Completed":
                task["Tier1_Completed_Date_Time"] = datetime.now().strftime("%B %d, %Y %I:%M %p")
            return True
    return False

# ======================================
# FRONTEND: LOGIN PAGE
# ======================================

def login_page():
    """Frontend: Login page UI"""
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h1 style='color: #2c3e50; margin-bottom: 0.5rem;'>🚀 ARMS Workflow Management</h1>
        <p style='color: #7f8c8d; margin-bottom: 2rem;'>Enterprise Task Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔐 User Login")
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Login", use_container_width=True, type="primary"):
                user = authenticate(username, password)  # Backend call
                if user:
                    # Backend state update
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    st.session_state.user_role = user["role"]
                    st.session_state.user_name = user["name"]
                    st.success(f"✅ Welcome {user['name']}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        with col_btn2:
            if st.button("Reset", use_container_width=True):
                st.rerun()
        
        with st.expander("ℹ️ Demo Credentials"):
            st.write("**Manager:** admin / admin123")
            st.write("**Analysts:** nisarg / nisarg123, komal / komal123")

# ======================================
# FRONTEND: DASHBOARD
# ======================================

def tab_dashboard():
    """Frontend: Dashboard with metrics"""
    st.markdown("### 📊 Dashboard Overview")
    
    # Backend data fetch
    total_tasks = len(st.session_state.tasks)
    pending_tasks = len([t for t in st.session_state.tasks if t["Status"] == "Pending"])
    my_tasks = len([t for t in st.session_state.tasks 
                   if t["Assigned_User"] == st.session_state.user_name and t["Status"] != "Completed"])
    completed_tasks = len([t for t in st.session_state.tasks if t["Status"] == "Completed"])
    
    # Frontend: Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card-enterprise">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value-enterprise">{pending_tasks}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label-enterprise">Available Tasks</div>', unsafe_allow_html=True)
        
        # Frontend: Get Next Task button
        next_task = get_next_task()  # Backend call
        if next_task and st.session_state.user_role == "analyst":
            if st.button("🚀 Get Next Task", key="get_next_dashboard", use_container_width=True):
                assign_task_to_user(next_task["Task_ID"], st.session_state.user_name)  # Backend call
                st.success(f"Task #{next_task['Task_ID']} assigned!")
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card-enterprise">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value-enterprise">{my_tasks}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label-enterprise">My Tasks</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card-enterprise">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value-enterprise">{total_tasks}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label-enterprise">Total Tasks</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card-enterprise">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value-enterprise">{completed_tasks}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label-enterprise">Completed</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Frontend: Charts
    st.markdown("### 📈 Recent Activity")
    col1, col2 = st.columns(2)
    
    with col1:
        df = pd.DataFrame(st.session_state.tasks)  # Backend data
        if not df.empty and 'Status' in df.columns:
            status_counts = df["Status"].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index, 
                        title="Task Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not df.empty and 'Priority' in df.columns:
            priority_counts = df["Priority"].value_counts()
            fig = px.bar(x=priority_counts.index, y=priority_counts.values,
                        title="Tasks by Priority", color=priority_counts.index)
            st.plotly_chart(fig, use_container_width=True)

# ======================================
# FRONTEND: TASK MANAGEMENT
# ======================================

def tab_task_management():
    """Frontend: Task management interface"""
    st.markdown("### 📋 Task Management")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        view_option = st.selectbox("View", ["All Tasks", "My Tasks", "Pending", "In Progress"])
    
    with col2:
        priority_filter = st.multiselect("Priority", ["High", "Medium", "Low"], 
                                        default=["High", "Medium", "Low"])
    
    with col3:
        task_type_filter = st.multiselect("Task Type", ["Tier I", "Tier II"], 
                                         default=["Tier I", "Tier II"])
    
    # Backend: Filter tasks
    filtered_tasks = st.session_state.tasks.copy()
    
    if view_option == "My Tasks":
        filtered_tasks = [t for t in filtered_tasks if t["Assigned_User"] == st.session_state.user_name]
    elif view_option == "Pending":
        filtered_tasks = [t for t in filtered_tasks if t["Status"] == "Pending"]
    elif view_option == "In Progress":
        filtered_tasks = [t for t in filtered_tasks if t["Status"] == "In Progress"]
    
    filtered_tasks = [t for t in filtered_tasks 
                     if t["Priority"] in priority_filter and t["Task_Type"] in task_type_filter]
    
    # Frontend: Display tasks
    st.markdown(f"#### {view_option} ({len(filtered_tasks)} tasks)")
    
    if not filtered_tasks:
        st.info("No tasks match the current filters.")
    else:
        for task in filtered_tasks:
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                st.write(f"**#{task['Task_ID']}** - {task['Company_Name']}")
            
            with col2:
                st.write(f"**Assigned:** {task['Assigned_User']}")
            
            with col3:
                status_class = task['Status'].lower().replace(' ', '-')
                st.markdown(f'<span class="status-badge status-{status_class}">{task["Status"]}</span>', 
                           unsafe_allow_html=True)
            
            with col4:
                priority_class = task['Priority'].lower()
                st.markdown(f'<span class="status-badge priority-{priority_class}">{task["Priority"]}</span>', 
                           unsafe_allow_html=True)
            
            # Actions
            if task["Status"] == "Pending" and task["Assigned_User"] == "Unassigned":
                if st.button("Accept", key=f"accept_{task['Task_ID']}"):
                    assign_task_to_user(task["Task_ID"], st.session_state.user_name)  # Backend call
                    st.rerun()
            
            st.markdown("---")

# ======================================
# FRONTEND: MAIN APP
# ======================================

def main_app():
    """Frontend: Main application after login"""
    
    st.markdown(f"""
    <div class="enterprise-header">
        <h1 style="margin:0; color:white;">🚀 ARMS Workflow Management System</h1>
        <p style="margin:0; opacity:0.9;">Welcome, {st.session_state.user_name} ({st.session_state.user_role.title()})</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    tabs = st.tabs(["📊 Dashboard", "📋 Task Management", "👥 Team"])
    
    with tabs[0]:
        tab_dashboard()
    
    with tabs[1]:
        tab_task_management()
    
    with tabs[2]:
        st.markdown("### 👥 Team Performance")
        st.info("Team analytics coming soon...")
    
    # Logout
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.rerun()

# ======================================
# MAIN EXECUTION (ROUTING)
# ======================================

def main():
    """Main routing function"""
    initialize_session_state()  # Initialize backend
    
    if not st.session_state.authenticated:
        login_page()  # Show frontend login
    else:
        main_app()  # Show frontend app

if __name__ == "__main__":
    main()
