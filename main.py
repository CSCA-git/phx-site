import streamlit as st
import json
import time
from github import Auth, Github
from g4f.client import Client

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Phoenix EC | CSCA Ecosystem",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ACCESS KEYS ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
REPO_NAME = st.secrets.get("REPO_NAME", "CSCA-git/the_db")
FILE_PATH = "db.json"

# --- DATABASE INTEGRATION ---
@st.cache_resource
def get_github_repo():
    auth = Auth.Token(GITHUB_TOKEN)
    return Github(auth=auth).get_repo(REPO_NAME)

def load_db():
    try:
        repo = get_github_repo()
        contents = repo.get_contents(FILE_PATH, ref="main")
        return json.loads(contents.decoded_content.decode("utf-8")), contents.sha
    except Exception as e:
        st.error(f"Load error: {e}")
        return {"users": {}}, None

def save_db(data, sha=None):
    try:
        repo = get_github_repo()
        contents = repo.get_contents(FILE_PATH, ref="main")
        result = repo.update_file(
            path=FILE_PATH, 
            message="Auto-update DB via Streamlit",
            content=json.dumps(data, indent=4, ensure_ascii=False),
            sha=contents.sha,
            branch="main"
        )
        return result["content"].sha
    except Exception as e:
        st.error(f"Save error: {e}")
        return sha

# --- SESSION STATE INITIALIZATION ---
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "full_exam_active" not in st.session_state:
    st.session_state.full_exam_active = False

db_data, db_sha = load_db()
if "db_sha" not in st.session_state:
    st.session_state.db_sha = db_sha

def sync_progress():
    st.session_state.db_sha = save_db(db_data, st.session_state.db_sha)

# --- DESIGN TOKENS WITH DARK MODE FIX & EXAM STYLES ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,600;8..60,700;8..60,800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&family=Sora:wght@600;700;800&display=swap');

    :root {
        --lacquer: #A8281F;
        --lacquer-dark: #7A1D17;
        --gold: #C08829;
        --jade: #1F6F5C;
        --ink: #241C18;
        --paper: #FBF6EE;
        --paper-alt: #F3EBDA;
        --hairline: #E4D8C0;
        --primary: #2F4CDD;
        --primary-dark: #1B2E99;
        --mint: #1FAA6A;
        --amber: #F2A93B;
        --crimson: #E4483C;
    }

    html, body, [class*="css"], .stApp { 
        font-family: 'Inter', sans-serif !important; 
        color: var(--ink) !important; 
        background-color: var(--paper) !important; 
    }

    h1, h2, h3, h4, h5, h6 { 
        font-family: 'Source Serif 4', serif !important; 
        color: var(--lacquer-dark) !important;
        letter-spacing: -0.01em; 
    }

    p, span, label, div { color: var(--ink); }

    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div,
    .stTextInput input, 
    .stSelectbox div[role="combobox"],
    textarea {
        background-color: #FFFFFF !important;
        color: #241C18 !important;
        border-color: var(--hairline) !important;
    }

    input, textarea, select {
        color: #241C18 !important;
        -webkit-text-fill-color: #241C18 !important;
    }

    ul[data-baseweb="menu"] { background-color: #FFFFFF !important; }
    ul[data-baseweb="menu"] li { color: #241C18 !important; }

    button[data-baseweb="tab"] p { color: var(--ink) !important; }
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: var(--lacquer) !important;
        font-weight: bold;
    }

    .hero-eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem; font-weight: 600; letter-spacing: 0.14em;
        text-transform: uppercase; color: var(--jade) !important; margin-bottom: 6px;
    }
    .hero-title {
        font-family: 'Source Serif 4', serif;
        font-size: 3.4rem; font-weight: 800; line-height: 1.05;
        color: var(--lacquer-dark) !important; margin-bottom: 10px;
    }
    .hero-sub {
        font-size: 1.15rem; color: #5B4E42 !important; font-weight: 400;
        line-height: 1.55; margin-bottom: 28px; max-width: 780px;
    }

    .chop {
        display: inline-flex; align-items: center; justify-content: center;
        width: 64px; height: 64px; border-radius: 10px;
        background: var(--lacquer); color: #FBF6EE !important;
        font-family: 'Source Serif 4', serif; font-weight: 800; font-size: 0.95rem;
        transform: rotate(-6deg);
        box-shadow: 0 6px 14px -4px rgba(122,29,23,0.45);
        border: 2px solid rgba(251,246,238,0.35);
        margin-bottom: 14px;
    }
    .chop-sm {
        display: inline-flex; align-items: center; justify-content: center;
        padding: 3px 12px; border-radius: 6px; background: var(--lacquer);
        color: #FBF6EE !important; font-family: 'JetBrains Mono', monospace; font-weight: 600;
        font-size: 0.72rem; letter-spacing: 0.06em; text-transform: uppercase;
        transform: rotate(-3deg); margin-bottom: 10px;
    }

    .chat-window-outer {
        background: #FFFFFF !important; border: 1px solid var(--hairline);
        border-radius: 14px; box-shadow: 0 12px 30px -12px rgba(36,28,24,0.18);
        overflow: hidden; margin-bottom: 20px;
    }
    .chat-window-header {
        background: linear-gradient(120deg, var(--lacquer) 0%, var(--lacquer-dark) 100%);
        color: #FBF6EE !important; padding: 14px 20px;
        display: flex; align-items: center; justify-content: space-between;
        font-weight: 600; font-size: 1.02rem;
        border-bottom: 3px solid var(--gold);
    }
    .chat-window-header * { color: #FBF6EE !important; }
    .chat-status-dot {
        height: 9px; width: 9px; background-color: #4ADE80; border-radius: 50%;
        display: inline-block; margin-right: 8px;
        box-shadow: 0 0 0 3px rgba(74,222,128,0.25);
    }

    .feature-card {
        background: #FFFFFF !important; border: 1px solid var(--hairline);
        border-radius: 14px; padding: 26px; height: 100%;
        box-shadow: 0 8px 20px -10px rgba(36,28,24,0.12);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .feature-card p, .feature-card h3 { color: var(--ink) !important; }
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 14px 28px -12px rgba(36,28,24,0.22);
    }
    .price-tag {
        font-family: 'Source Serif 4', serif;
        font-size: 1.9rem; font-weight: 800; color: var(--lacquer-dark) !important;
        margin-top: 10px;
    }

    .hairline { border: none; border-top: 1px solid var(--hairline); margin: 28px 0; }

    section[data-testid="stSidebar"] { 
        background: var(--paper-alt) !important; 
        border-right: 1px solid var(--hairline); 
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. PUBLIC LANDING PAGE (NO LOGIN)
# ==========================================
if st.session_state.page == "landing":
    with st.sidebar:
        st.markdown('<div class="chop">凤</div>', unsafe_allow_html=True)
        st.title("Phoenix EC Portal")
        st.markdown("<hr class='hairline'>", unsafe_allow_html=True)
        if st.button("🔐 Student Portal Login", width='stretch', type="primary"):
            st.session_state.page = "auth"
            st.rerun()
        st.markdown("<hr class='hairline'>", unsafe_allow_html=True)
        st.markdown("### 📍 Contact Info")
        st.markdown("🏢 Komitas Ave. 49/2, Yerevan\n\n📞 055 388801\n\n✉️ phoenix.ec@mail.ru")

    st.markdown('<p class="hero-eyebrow">CSCA Exam Prep · Chinese Higher Education</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-title">Phoenix Educational Center</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">The official ecosystem for CSCA preparation and admission into Chinese universities. Guided by management with a dual PhD background in history and philology, we run a strategic, culturally grounded academic program from Yerevan.</p>', unsafe_allow_html=True)

    t1, t2, t3, t4, t5 = st.tabs(["🤖 Public AI Advisor", "📚 CSCA Courses", "🇨🇳 Phoenix Initiatives", "🏛️ Target Universities", "📍 Contact Us"])

    with t1:
        st.markdown("""<div class="chat-window-outer"><div class="chat-window-header"><div><span class="chat-status-dot"></span> <b>Phoenix Public AI</b></div><div>Yerevan • Komitas 49/2</div></div></div>""", unsafe_allow_html=True)
        if "pub_chat" not in st.session_state:
            st.session_state.pub_chat = []

        chat_box = st.container(height=350)
        with chat_box:
            for msg in st.session_state.pub_chat:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about our courses, Shanghai AI trip, or CSCA..."):
            st.session_state.pub_chat.append({"role": "user", "content": prompt})
            with chat_box:
                st.chat_message("user").markdown(prompt)
                with st.chat_message("assistant", avatar="🦅"):
                    with st.spinner("Responding..."):
                        try:
                            client = Client()
                            sys_inst = """You are the public advisor for Phoenix Educational Center.
Address: Komitas Ave. 49/2 (Adjacent to Komitas Market), Yerevan, Armenia, 0014. Phone: 055 388801. Email: phoenix.ec@mail.ru.
Key Info: CSCA Exam is June 27, 2026. We offer prep courses ($26.90, $129.90, $380.00). We partner with Beijing Dacheng Future Academy. We organize an AI trip to Shanghai in late October. Be concise, polite, and helpful in English."""
                            messages = [{"role": "system", "content": sys_inst}]
                            for m in st.session_state.pub_chat:
                                messages.append({"role": m["role"], "content": m["content"]})

                            response = client.chat.completions.create(model="gemini", messages=messages)
                            answer = response.choices[0].message.content
                            st.markdown(answer)
                            st.session_state.pub_chat.append({"role": "assistant", "content": answer})
                        except Exception as e:
                            st.error(f"AI Error: {e}")

    with t2:
        st.markdown("### 📚 Official CSCA Prep Packages")
        col1, col2, col3 = st.columns(3, gap="large")
        with col1: st.markdown('<div class="feature-card"><span class="chop-sm">Foundation</span><h3>📘 CSCA Study Package</h3><p>Self-paced prep, mock tests &amp; formula guides.</p><div class="price-tag">$26.90</div></div>', unsafe_allow_html=True)
        with col2: st.markdown('<div class="feature-card"><span class="chop-sm">Popular</span><h3>🎥 Video Course</h3><p>Comprehensive Math &amp; Physics video modules.</p><div class="price-tag">$129.90</div></div>', unsafe_allow_html=True)
        with col3: st.markdown('<div class="feature-card"><span class="chop-sm">Intensive</span><h3>🚀 15-Day Bootcamp</h3><p>Live study groups and TA support.</p><div class="price-tag">$380.00</div></div>', unsafe_allow_html=True)

    with t3:
        st.markdown("### 🇨🇳 Phoenix Special Programs")
        prog_col1, prog_col2, prog_col3 = st.columns(3)
        with prog_col1: st.markdown('<div class="feature-card"><h3>🏫 Beijing Dacheng Academy</h3><p>Exclusive partnerships and school visits to our partner international school in Beijing, China.</p></div>', unsafe_allow_html=True)
        with prog_col2: st.markdown('<div class="feature-card"><h3>🤖 AI Trip in Shanghai</h3><p>Join our immersive tech and Artificial Intelligence trip to Shanghai during the last week of October.</p></div>', unsafe_allow_html=True)
        with prog_col3: st.markdown('<div class="feature-card"><h3>🎓 Scholarships</h3><p>Full advisory services for securing Bachelor\'s and Master\'s scholarships.</p></div>', unsafe_allow_html=True)

    with t4:
        st.markdown("### 🏛️ Target Universities")
        st.write("Leveraging our extensive network of admissions contacts across China, we streamline your path to prestigious institutions.")
        u_col1, u_col2, u_col3 = st.columns(3)
        with u_col1:
            st.image("https://images.unsplash.com/photo-1562774053-701939374585?ixlib=rb-4.0.3&w=600&q=80", width='stretch')
            st.markdown("#### Fudan University")
        with u_col2:
            st.image("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?ixlib=rb-4.0.3&w=600&q=80", width='stretch')
            st.markdown("#### Jilin University")
        with u_col3:
            st.image("https://www.portalchina.ru/wp-content/uploads/2025/09/izobrazhenie_2025-09-26_194922752.png", width='stretch')
            st.markdown("#### Civil Aviation University of China")

    with t5:
        st.markdown("### 📍 Phoenix Educational Center")
        st.markdown("**🏢 Address:** Komitas Ave. 49/2 (Adjacent to Komitas Market), Yerevan, Armenia, 0014")
        st.markdown("**📞 Phone:** 055 388801")
        st.markdown("**✉️ Email:** phoenix.ec@mail.ru")
        st.markdown("**📅 Important Date:** CSCA Exam scheduled for June 27, 2026 (Registration via csca.cn).")

# ==========================================
# 2. AUTHENTICATION PAGE
# ==========================================
elif st.session_state.page == "auth":
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "landing"
        st.rerun()

    st.markdown('<div style="text-align:center;"><span class="chop">凤</span></div>', unsafe_allow_html=True)
    st.markdown('<p class="hero-title" style="text-align: center;">Student Portal</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_reg = st.tabs(["🔑 Login", "📝 Register"])
        with tab_login:
            with st.form("login_form"):
                log_user = st.text_input("Username")
                log_pass = st.text_input("Password", type="password")
                if st.form_submit_button("Sign In"):
                    if log_user in db_data["users"] and db_data["users"][log_user]["password"] == log_pass:
                        st.session_state.logged_in = True
                        st.session_state.username = log_user
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        with tab_reg:
            with st.form("reg_form"):
                reg_user = st.text_input("Username")
                reg_pass = st.text_input("Password", type="password")
                reg_target = st.selectbox("Target University", ["Fudan University", "Jilin University", "Civil Aviation University of China"])
                reg_gpa = st.slider("Current GPA", 50, 100, 80)
                if st.form_submit_button("Create Account"):
                    if reg_user in db_data["users"]:
                        st.error("Username already taken!")
                    elif reg_user and reg_pass:
                        db_data["users"][reg_user] = {
                            "password": reg_pass, "target_uni": reg_target, "gpa": reg_gpa,
                            "xp": 0, "level": 1, "chat_history": [], "mistakes": []
                        }
                        sync_progress()
                        st.success("Registration successful! You can now log in.")

# ==========================================
# 3. PRIVATE STUDENT DASHBOARD
# ==========================================
elif st.session_state.page == "dashboard" and st.session_state.logged_in:
    user_profile = db_data["users"][st.session_state.username]
    if "mistakes" not in user_profile:
        user_profile["mistakes"] = []

    with st.sidebar:
        st.markdown('<div class="chop">凤</div>', unsafe_allow_html=True)
        st.markdown(f"### 🎓 {st.session_state.username}")
        st.markdown(f"**🎯 Target:** {user_profile['target_uni']}")

        current_level = (user_profile["xp"] // 100) + 1
        if current_level != user_profile["level"]:
            user_profile["level"] = current_level
            sync_progress()

        xp_in_level = user_profile["xp"] % 100
        st.progress(xp_in_level / 100.0, text=f"Level {user_profile['level']} (XP: {user_profile['xp']})")

        st.markdown("<hr class='hairline'>", unsafe_allow_html=True)
        if st.button("🚪 Logout", width='stretch'):
            sync_progress()
            st.session_state.logged_in = False
            st.session_state.page = "landing"
            st.rerun()

    st.markdown('<p class="hero-eyebrow">Gamified Training Hub</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="hero-title">Welcome back, {st.session_state.username}!</p>', unsafe_allow_html=True)

    dash_t1, dash_t2, dash_t3, dash_t4, dash_t5 = st.tabs([
        "⚡ Quick Practice", "🤖 AI Full Mock Exam", "🧠 AI Mentor", "📐 Formula Library & AI", "❌ Mistakes Bank"
    ])

    # -------------------------------------------------------------
    # TAB 1: QUICK AI PRACTICE
    # -------------------------------------------------------------
    with dash_t1:
        st.write("Generate quick single questions to build up your streak and earn fast XP!")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.info("📌 **Mathematics**")
            subj1 = st.selectbox("Select Topic", ["Algebra", "Vectors", "Calculus", "Geometry"], key="m1")
            if st.button("Start Quick Math"):
                st.session_state.quiz_subject = f"Math - {subj1}"
                st.session_state.quiz_data = None
        with c2:
            st.warning("⚡ **Physics**")
            subj2 = st.selectbox("Select Topic", ["Kinematics", "Dynamics", "Thermodynamics", "Optics"], key="m2")
            if st.button("Start Quick Physics"):
                st.session_state.quiz_subject = f"Physics - {subj2}"
                st.session_state.quiz_data = None
        with c3:
            st.error("🧪 **Chemistry**")
            subj3 = st.selectbox("Select Topic", ["Organic", "Inorganic", "Stoichiometry"], key="m3")
            if st.button("Start Quick Chemistry", disabled=user_profile["level"] < 2):
                st.session_state.quiz_subject = f"Chemistry - {subj3}"
                st.session_state.quiz_data = None
            if user_profile["level"] < 2: st.caption("🔒 Unlocks at Level 2")

        st.markdown("<hr class='hairline'>", unsafe_allow_html=True)

        if hasattr(st.session_state, 'quiz_subject'):
            st.markdown(f"### 📝 Active Test: {st.session_state.quiz_subject}")
            if st.session_state.quiz_data is None:
                with st.spinner("AI is generating a unique question with detailed explanation..."):
                    try:
                        client = Client()
                        prompt = f"""Generate ONE multiple-choice question for the CSCA entrance exam about {st.session_state.quiz_subject}. Output EXACTLY in this strict format:
QUESTION: [text]
A: [text]
B: [text]
C: [text]
D: [text]
CORRECT: [A/B/C/D]
EXPLANATION: [Step-by-step solution]"""
                        response = client.chat.completions.create(model="gemini", messages=[{"role": "user", "content": prompt}])
                        lines = response.choices[0].message.content.strip().split('\n')
                        q_dict = {}
                        for line in lines:
                            if line.startswith("QUESTION:"): q_dict["q"] = line.replace("QUESTION:", "").strip()
                            elif line.startswith("A:"): q_dict["a"] = line.replace("A:", "").strip()
                            elif line.startswith("B:"): q_dict["b"] = line.replace("B:", "").strip()
                            elif line.startswith("C:"): q_dict["c"] = line.replace("C:", "").strip()
                            elif line.startswith("D:"): q_dict["d"] = line.replace("D:", "").strip()
                            elif line.startswith("CORRECT:"): q_dict["ans"] = line.replace("CORRECT:", "").strip()
                            elif line.startswith("EXPLANATION:"): q_dict["exp"] = line.replace("EXPLANATION:", "").strip()

                        if "q" in q_dict and "ans" in q_dict:
                            st.session_state.quiz_data = q_dict
                        else: st.error("Failed to parse AI question. Try again.")
                    except Exception as e: st.error(f"AI connection failed: {e}")

            if st.session_state.quiz_data:
                q = st.session_state.quiz_data
                st.write(f"**{q.get('q')}**")
                with st.form("quiz_form"):
                    user_ans = st.radio("Select your answer:", [f"A) {q.get('a')}", f"B) {q.get('b')}", f"C) {q.get('c')}", f"D) {q.get('d')}"])
                    if st.form_submit_button("Submit Answer"):
                        selected_letter = user_ans[0]
                        if selected_letter == q.get("ans"):
                            user_profile["xp"] += 20
                            sync_progress()
                            st.success(f"Correct! 🎉 +20 XP. You now have {user_profile['xp']} XP.")
                            if q.get("exp"): st.info(f"💡 **Explanation:** {q.get('exp')}")
                            st.balloons()
                            del st.session_state.quiz_subject
                            st.session_state.quiz_data = None
                        else:
                            st.error(f"Incorrect. The correct answer was {q.get('ans')}.")
                            if q.get("exp"): st.warning(f"💡 **Explanation:** {q.get('exp')}")
                            user_profile["mistakes"].append({
                                "subject": st.session_state.quiz_subject,
                                "question": q.get('q'),
                                "correct_ans": q.get(q.get('ans').lower()),
                                "explanation": q.get('exp', 'No explanation provided.')
                            })
                            sync_progress()
                            del st.session_state.quiz_subject
                            st.session_state.quiz_data = None

    # -------------------------------------------------------------
    # TAB 2: DYNAMIC AI FULL MOCK EXAM
    # -------------------------------------------------------------
    with dash_t2:
        st.markdown("### 🏛️ Dynamic AI Full Mock Exam Generator")
        st.write("Generate a full 10-question timed exam for **ANY subject and topic** powered by AI.")

        col_cfg1, col_cfg2 = st.columns(2)
        with col_cfg1:
            exam_subject = st.selectbox("Select Exam Subject:", [
                "Mathematics", "Physics", "Chemistry", "Biology", 
                "CSCA General Science", "Chinese History & Culture", "Computer Science"
            ])
        with col_cfg2:
            exam_topic = st.text_input("Specific Topic / Focus Area:", value="General Overview")

        if st.button("✨ Generate AI Full Mock Exam", type="primary"):
            with st.spinner("AI is generating your full exam paper with 10 structured questions..."):
                try:
                    client = Client()
                    exam_prompt = f"""Generate a full exam of EXACTLY 10 multiple-choice questions for CSCA on Subject: '{exam_subject}', Topic: '{exam_topic}'.
Format your response purely as a valid JSON array of 10 objects, where each object has:
"id": number (1 to 10),
"question": string,
"choices": array of 4 strings (options A, B, C, D),
"correct": number (0 for A, 1 for B, 2 for C, 3 for D),
"explanation": string (step-by-step solution)
Output ONLY the JSON array and no other text or markdown codeblocks."""

                    response = client.chat.completions.create(model="gemini", messages=[{"role": "user", "content": exam_prompt}])
                    raw_txt = response.choices[0].message.content.strip()
                    if raw_txt.startswith("```json"): raw_txt = raw_txt.replace("```json", "").replace("```", "").strip()
                    elif raw_txt.startswith("```"): raw_txt = raw_txt.replace("```", "").strip()
                    
                    generated_bank = json.loads(raw_txt)
                    
                    st.session_state.full_exam_active = True
                    st.session_state.exam_bank = generated_bank
                    st.session_state.exam_answers = [None] * len(generated_bank)
                    st.session_state.exam_flags = [False] * len(generated_bank)
                    st.session_state.exam_current = 0
                    st.session_state.exam_submitted = False
                    st.session_state.exam_start_time = time.time()
                    st.success("Exam paper generated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating AI Exam: {e}. Please try again.")

        if st.session_state.get("full_exam_active", False):
            st.markdown("<hr class='hairline'>", unsafe_allow_html=True)
            q_bank = st.session_state.exam_bank
            curr_idx = st.session_state.exam_current

            elapsed = int(time.time() - st.session_state.exam_start_time)
            remaining = max(0, (20 * 60) - elapsed)
            mins, secs = remaining // 60, remaining % 60
            st.markdown(f"⏱️ **Time Remaining:** `{mins:02d}:{secs:02d}` | 📊 **Progress:** {sum(1 for a in st.session_state.exam_answers if a is not None)}/{len(q_bank)} Answered")

            if not st.session_state.exam_submitted:
                st.write("**Question Grid:**")
                grid_cols = st.columns(len(q_bank))
                for i in range(len(q_bank)):
                    if grid_cols[i].button(f"{i+1}", key=f"ai_qcell_{i}"):
                        st.session_state.exam_current = i
                        st.rerun()

                q_obj = q_bank[curr_idx]
                st.markdown(f"#### Question {curr_idx + 1} of {len(q_bank)}")
                st.markdown(f"**{q_obj['question']}**")

                opts = q_obj["choices"]
                curr_selected = st.session_state.exam_answers[curr_idx]
                
                selected_opt = st.radio("Choose Option:", opts, key=f"radio_ai_q_{curr_idx}")
                st.session_state.exam_answers[curr_idx] = opts.index(selected_opt)

                col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 2])
                with col_nav1:
                    if st.button("⬅️ Previous", disabled=curr_idx == 0):
                        st.session_state.exam_current -= 1
                        st.rerun()
                with col_nav2:
                    if st.button("Next ➡️", disabled=curr_idx == len(q_bank)-1):
                        st.session_state.exam_current += 1
                        st.rerun()
                with col_nav3:
                    if st.button("🔖 Flag for Review"):
                        st.session_state.exam_flags[curr_idx] = not st.session_state.exam_flags[curr_idx]
                        st.rerun()

                st.markdown("---")
                if st.button("📥 Finish & Submit Exam", type="primary"):
                    st.session_state.exam_submitted = True
                    st.rerun()

            else:
                correct_count = sum(1 for i in range(len(q_bank)) if st.session_state.exam_answers[i] == q_bank[i]["correct"])
                total_score = int((correct_count / len(q_bank)) * 100)
                
                st.balloons()
                st.success(f"🎉 Exam Submitted! Your Score: **{total_score} / 100** ({correct_count}/{len(q_bank)} Correct)")
                user_profile["xp"] += total_score
                sync_progress()

                st.markdown("### 🔍 Detailed Solution Review")
                for i, q in enumerate(q_bank):
                    ans = st.session_state.exam_answers[i]
                    is_correct = (ans == q["correct"])
                    if not is_correct:
                        user_profile["mistakes"].append({
                            "subject": exam_subject,
                            "question": q["question"],
                            "correct_ans": q["choices"][q["correct"]],
                            "explanation": q.get("explanation", "Step-by-step solution")
                        })
                    with st.expander(f"Question {i+1}: {'✅ Correct' if is_correct else '❌ Incorrect'}"):
                        st.write(f"**Question:** {q['question']}")
                        st.write(f"**Your Answer:** {q['choices'][ans] if ans is not None else 'None'}")
                        st.write(f"**Correct Answer:** {q['choices'][q['correct']]}")
                        st.write(f"**Explanation:** {q.get('explanation', '')}")

                sync_progress()

                if st.button("🔄 Generate Another Exam"):
                    st.session_state.full_exam_active = False
                    st.rerun()

    # -------------------------------------------------------------
    # TAB 3: PERSONAL AI MENTOR
    # -------------------------------------------------------------
    with dash_t3:
        st.markdown("""<div class="chat-window-outer"><div class="chat-window-header"><div><span class="chat-status-dot"></span> <b>Personal AI Mentor</b></div><div>Secure Student Mode</div></div></div>""", unsafe_allow_html=True)
        sys_inst_priv = f"""You are the personal AI tutor for Phoenix Educational Center. Student Name: {st.session_state.username}. Target Uni: {user_profile['target_uni']}.
Help them prepare for the CSCA exam. Be engaging, praise progress, and act as a dedicated academic mentor in English."""

        chat_box = st.container(height=350)
        with chat_box:
            if not user_profile["chat_history"]:
                st.info(f"Hi {st.session_state.username}! I am your personal tutor. Ask me anything about CSCA prep or {user_profile['target_uni']}.")
            for msg in user_profile["chat_history"]:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])

        if prompt := st.chat_input("Ask your mentor a question (earn +5 XP)..."):
            user_profile["chat_history"].append({"role": "user", "content": prompt})
            with chat_box:
                st.chat_message("user").markdown(prompt)
                with st.chat_message("assistant", avatar="🦅"):
                    with st.spinner("Thinking..."):
                        try:
                            client = Client()
                            messages = [{"role": "system", "content": sys_inst_priv}]
                            for m in user_profile["chat_history"]: messages.append({"role": m["role"], "content": m["content"]})
                            response = client.chat.completions.create(model="gemini", messages=messages)
                            answer = response.choices[0].message.content
                            st.markdown(answer)
                            user_profile["chat_history"].append({"role": "assistant", "content": answer})
                            user_profile["xp"] += 5
                            sync_progress()
                        except Exception as e: st.error(f"AI Error: {e}")

    # -------------------------------------------------------------
    # TAB 4: EXTENDED FORMULA SHEET & AI FORMULA SEARCH
    # -------------------------------------------------------------
    with dash_t4:
        st.markdown("### 📐 CSCA Comprehensive Formula Library & Smart Finder")
        
        st.info("🤖 **AI Formula Finder:** Type what you need to calculate across any subject (Math, Physics, Chemistry, CS), and AI will extract the exact formula.")
        formula_query = st.text_input("Search Formula by Problem Description:", placeholder="e.g. ideal gas law or projectile motion max height")
        if formula_query:
            with st.spinner("Finding required formula..."):
                try:
                    client = Client()
                    f_prompt = f"Provide ONLY the exact LaTeX mathematical/scientific formula and variable breakdown for: {formula_query}. Be direct and concise."
                    f_resp = client.chat.completions.create(model="gemini", messages=[{"role": "user", "content": f_prompt}])
                    st.success("🎯 **Found Formula:**")
                    st.markdown(f_resp.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error finding formula: {e}")

        st.markdown("<hr class='hairline'>", unsafe_allow_html=True)
        
        f_tab1, f_tab2, f_tab3 = st.tabs(["Mathematics", "Physics", "Chemistry"])
        with f_tab1:
            st.markdown("#### Algebra & Quadratic Equations")
            st.latex(r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}")
            st.markdown("#### Arithmetic & Geometric Sequences")
            st.latex(r"a_n = a_1 + (n-1)d, \quad S_n = \frac{n(a_1 + a_n)}{2}")
            st.latex(r"a_n = a_1 \cdot r^{n-1}, \quad S_n = a_1 \frac{1 - r^n}{1 - r}")
            st.markdown("#### Analytic Geometry (Conics)")
            st.latex(r"\text{Ellipse: } \frac{x^2}{a^2} + \frac{y^2}{b^2} = 1, \quad c^2 = a^2 - b^2, \quad e = \frac{c}{a}")
            st.latex(r"\text{Parabola: } y^2 = 4px \implies \text{Focus: } (p,0), \quad \text{Directrix: } x = -p")

        with f_tab2:
            st.markdown("#### Kinematics & Newton's Laws")
            st.latex(r"v = v_0 + at, \quad s = v_0 t + \frac{1}{2}at^2, \quad v^2 = v_0^2 + 2as")
            st.latex(r"F = m \cdot a, \quad p = m \cdot v, \quad J = \Delta p = F \cdot \Delta t")

        with f_tab3:
            st.markdown("#### Ideal Gas & Stoichiometry")
            st.latex(r"PV = nRT, \quad n = \frac{m}{M} = \frac{V}{V_m}")
            st.latex(r"C = \frac{n}{V}, \quad pH = -\log_{10}[H^+]")

    # -------------------------------------------------------------
    # TAB 5: MISTAKES BANK
    # -------------------------------------------------------------
    with dash_t5:
        st.markdown("### ❌ Mistakes Bank & Review")
        if not user_profile["mistakes"]:
            st.success("Great job! You don't have any saved mistakes yet. Keep solving tests!")
        else:
            for idx, item in enumerate(user_profile["mistakes"]):
                with st.expander(f"📌 [{item['subject']}] {item['question']}"):
                    st.write(f"**Correct Answer:** {item['correct_ans']}")
                    st.write(f"**Explanation:** {item['explanation']}")
                    if st.button(f"Mark as Mastered #{idx}"):
                        user_profile["mistakes"].pop(idx)
                        sync_progress()
                        st.rerun()
