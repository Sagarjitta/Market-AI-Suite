import streamlit as st
from groq import Groq
import os, csv, requests
from datetime import datetime
import pandas as pd
from streamlit_lottie import st_lottie

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Sales Management",
    page_icon="📊",
    layout="wide"
)

DATA_FILE = "sales_data.csv"
USERS_FILE = "users.csv"

# ---------------- CSS ----------------
st.markdown("""
<style>
.main { animation: fadeIn .6s ease-in-out; }
@keyframes fadeIn {
    from { opacity:0; transform:translateY(10px); }
    to { opacity:1; transform:translateY(0); }
}
.card {
    background: rgba(255,255,255,.12);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 25px;
    box-shadow: 0 12px 35px rgba(0,0,0,.18);
}
.card:hover { transform: translateY(-6px); }
.login-box {
    max-width: 400px;
    margin: 80px auto;
    padding: 40px;
    background: rgba(255,255,255,.15);
    backdrop-filter: blur(14px);
    border-radius: 22px;
    box-shadow: 0 15px 45px rgba(0,0,0,.2);
}
</style>
""", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
def card_start():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

def card_end():
    st.markdown("</div>", unsafe_allow_html=True)

def show_loader(text):
    st.markdown(f"""
    <div class="card" style="text-align:center">
        <strong>{text}</strong><br><br>
        ⏳ AI is thinking...
    </div>
    """, unsafe_allow_html=True)

def load_lottie(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def app_header():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:15px;margin-bottom:25px;">
            <img src="https://cdn-icons-png.flaticon.com/512/1389/1389181.png" width="45">
            <h1 style="margin:0;">AI Sales Management</h1>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()

# ---------------- LOTTIES ----------------
l_campaign  = load_lottie("https://assets10.lottiefiles.com/packages/lf20_touohxv0.json")
l_pitch     = load_lottie("https://assets10.lottiefiles.com/packages/lf20_qp1q7mct.json")
l_lead      = load_lottie("https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json")
l_analytics = load_lottie("https://assets2.lottiefiles.com/packages/lf20_vnikrcia.json")

# ---------------- USER MANAGEMENT ----------------
def init_users_file():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["username", "password"])
            writer.writeheader()
            # Default user
            writer.writerow({"username": "admin", "password": "admin123"})

def verify_user(username, password):
    init_users_file()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username and row["password"] == password:
                return True
    return False

def register_user(username, password):
    init_users_file()
    # Check if user exists
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return False
    
    # Add new user
    with open(USERS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["username", "password"])
        writer.writerow({"username": username, "password": password})
    return True

# ---------------- DATA ----------------
def save_to_csv(row):
    exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not exists:
            writer.writeheader()
        writer.writerow(row)

def load_data():
    return pd.read_csv(DATA_FILE) if os.path.exists(DATA_FILE) else pd.DataFrame()

def delete_record(index):
    df = load_data()
    if not df.empty and 0 <= index < len(df):
        df = df.drop(index)
        df.to_csv(DATA_FILE, index=False)
        return True
    return False

# ---------------- GROQ ----------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_llm(prompt):
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert AI sales assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return res.choices[0].message.content

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_to(page):
    st.session_state.page = page

# ---------------- LOGIN PAGE ----------------
def login_page():
    st.markdown("""
    <div style="text-align:center;margin-top:50px;">
        <img src="https://cdn-icons-png.flaticon.com/512/1389/1389181.png" width="80">
        <h1>AI Sales Management</h1>
        <p style="color:#888;">Sign in to continue</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("🔐 Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Sign In", key="login_btn", use_container_width=True):
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        
        st.info("💡 Default credentials: admin / admin123")
    
    with tab2:
        st.subheader("📝 Register")
        new_username = st.text_input("Choose Username", key="reg_user")
        new_password = st.text_input("Choose Password", type="password", key="reg_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Create Account", key="reg_btn", use_container_width=True):
            if not new_username or not new_password:
                st.error("Please fill all fields")
            elif new_password != confirm_password:
                st.error("Passwords don't match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                if register_user(new_username, new_password):
                    st.success("Account created! Please login.")
                else:
                    st.error("Username already exists")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- HOME ----------------
def home():
    app_header()

    st.markdown(f"""
    <div style="padding:35px;border-radius:22px;
    background:linear-gradient(135deg,#667eea,#764ba2);
    color:white;margin-bottom:35px;">
    <h2>AI-powered Sales Accelerator</h2>
    <p>Campaigns • Pitches • Lead Scoring • Analytics</p>
    <p style="margin-top:15px;opacity:0.9;">👤 Logged in as: <strong>{st.session_state.username}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        card_start()
        st_lottie(l_campaign, height=110, key="lc")
        st.button("🚀 Campaign", key="hc", use_container_width=True,
                  on_click=go_to, args=("campaign",))
        card_end()

    with c2:
        card_start()
        st_lottie(l_pitch, height=110, key="lp")
        st.button("🎤 Pitch", key="hp", use_container_width=True,
                  on_click=go_to, args=("pitch",))
        card_end()

    with c3:
        card_start()
        st_lottie(l_lead, height=110, key="ll")
        st.button("🎯 Lead", key="hl", use_container_width=True,
                  on_click=go_to, args=("lead",))
        card_end()

    with c4:
        card_start()
        st_lottie(l_analytics, height=110, key="la")
        st.button("📊 Analytics", key="ha", use_container_width=True,
                  on_click=go_to, args=("analytics",))
        card_end()

# ---------------- CAMPAIGN ----------------
def campaign():
    app_header()
    st.header("📣 Campaign Generator")
    product = st.text_input("Product", key="cp")
    audience = st.text_area("Audience", key="ca")
    ctype = st.selectbox("Type", ["Email","Social","Ads"], key="ct")

    if st.button("Generate", key="cg"):
        show_loader("Generating campaign...")
        output = ask_llm(f"Create {ctype} campaign for {product} targeting {audience}")
        save_to_csv({"type":"campaign","input":product,"details":audience,
                     "output":output,"timestamp":datetime.now().isoformat()})
        st.success("Saved")
        st.markdown(f"<div class='card'>{output}</div>", unsafe_allow_html=True)

    st.button("⬅ Back", key="cb", on_click=go_to, args=("home",))

# ---------------- PITCH ----------------
def pitch():
    app_header()
    st.header("🎤 Sales Pitch")
    product = st.text_input("Product", key="pp")
    customer = st.text_input("Customer", key="pc")

    if st.button("Generate", key="pg"):
        show_loader("Creating pitch...")
        output = ask_llm(f"Create a pitch for {product} to {customer}")
        save_to_csv({"type":"pitch","input":product,"details":customer,
                     "output":output,"timestamp":datetime.now().isoformat()})
        st.success("Saved")
        st.markdown(f"<div class='card'>{output}</div>", unsafe_allow_html=True)

    st.button("⬅ Back", key="pb", on_click=go_to, args=("home",))

# ---------------- LEAD ----------------
def lead():
    app_header()
    st.header("🎯 Lead Scorer")
    info = st.text_area("Lead Info", key="li")

    if st.button("Score", key="ls"):
        show_loader("Scoring lead...")
        output = ask_llm(f"Score this lead 1-100:\n{info}")
        save_to_csv({"type":"lead","input":"Lead","details":info,
                     "output":output,"timestamp":datetime.now().isoformat()})
        st.success("Saved")
        st.markdown(f"<div class='card'>{output}</div>", unsafe_allow_html=True)

    st.button("⬅ Back", key="lb", on_click=go_to, args=("home",))

# ---------------- ANALYTICS ----------------
def analytics():
    app_header()
    st.header("📊 Analytics")
    df = load_data()

    if df.empty:
        st.info("No data yet")
        st.button("⬅ Back", key="ab", on_click=go_to, args=("home",))
        return

    c1,c2,c3 = st.columns(3)
    c1.metric("Campaigns", len(df[df.type=="campaign"]))
    c2.metric("Pitches", len(df[df.type=="pitch"]))
    c3.metric("Leads", len(df[df.type=="lead"]))

    st.bar_chart(df["type"].value_counts())
    
    # Data table with delete functionality
    st.subheader("📋 All Records")
    
    # Add index column for reference
    df_display = df.copy()
    df_display.insert(0, 'ID', range(len(df_display)))
    
    st.dataframe(df_display, use_container_width=True)
    
    # Delete functionality
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        record_id = st.number_input(
            "Enter Record ID to delete", 
            min_value=0, 
            max_value=len(df)-1 if len(df) > 0 else 0,
            step=1,
            key="delete_id"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Delete Record", key="delete_btn", type="primary"):
            if delete_record(record_id):
                st.success(f"Record {record_id} deleted successfully!")
                st.rerun()
            else:
                st.error("Failed to delete record")
    
    st.download_button("⬇ Download CSV", df.to_csv(index=False),
                       "sales_data.csv","text/csv", key="ad")

    st.button("⬅ Back", key="ab2", on_click=go_to, args=("home",))

# ---------------- ROUTER ----------------
if not st.session_state.logged_in:
    login_page()
else:
    {
        "home": home,
        "campaign": campaign,
        "pitch": pitch,
        "lead": lead,
        "analytics": analytics
    }[st.session_state.page]()