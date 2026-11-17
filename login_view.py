"""
login_view.py
Professional, high-aesthetic login and registration interface for Sign Language Studio.
Features frosted glassmorphism, dynamic animations, user-isolated data selection,
and 1-click quick demo access.
"""

import streamlit as st
import auth_manager
import user_data_manager


def inject_login_styles():
    st.markdown(
        """
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Hide default Streamlit clutter during auth */
        header[data-testid="stHeader"] {
            background: transparent !important;
        }
        [data-testid="stSidebar"] {
            display: none !important;
        }
        .main .block-container {
            max-width: 1200px !important;
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
        }

        /* Ambient Background */
        .stApp {
            background: radial-gradient(circle at 15% 20%, rgba(79, 70, 229, 0.18) 0%, transparent 45%),
                        radial-gradient(circle at 85% 75%, rgba(147, 51, 234, 0.16) 0%, transparent 45%),
                        radial-gradient(circle at 50% 50%, rgba(6, 182, 212, 0.08) 0%, transparent 60%),
                        #0b0f19 !important;
            color: #f1f5f9;
        }

        /* Hero Brand Card */
        .auth-hero-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.85));
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border-radius: 24px;
            padding: 34px 30px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            position: relative;
        }

        .auth-hero-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #6366f1, #a855f7, #06b6d4);
        }

        .brand-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(99, 102, 241, 0.35);
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #a5b4fc;
            margin-bottom: 20px;
        }

        .brand-title {
            font-size: 2.3rem;
            font-weight: 800;
            line-height: 1.15;
            background: linear-gradient(135deg, #ffffff 40%, #c7d2fe 80%, #93c5fd 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 14px;
        }

        .brand-subtitle {
            font-size: 1.05rem;
            color: #94a3b8;
            line-height: 1.6;
            margin-bottom: 28px;
        }

        .feature-grid {
            display: flex;
            flex-direction: column;
            gap: 16px;
            margin-top: 10px;
        }

        .feature-item {
            display: flex;
            align-items: flex-start;
            gap: 14px;
            padding: 14px 16px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            transition: all 0.25s ease;
        }

        .feature-item:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(99, 102, 241, 0.3);
            transform: translateX(4px);
        }

        .feature-icon-box {
            font-size: 1.3rem;
            width: 38px;
            height: 38px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(99, 102, 241, 0.15);
            border-radius: 10px;
            flex-shrink: 0;
        }

        .feature-text h4 {
            margin: 0;
            font-size: 0.95rem;
            font-weight: 600;
            color: #f8fafc;
        }

        .feature-text p {
            margin: 3px 0 0 0;
            font-size: 0.82rem;
            color: #94a3b8;
            line-height: 1.4;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-top: 28px;
            padding: 8px 16px;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.25);
            border-radius: 9999px;
            font-size: 0.8rem;
            color: #6ee7b7;
            font-weight: 600;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 10px #10b981;
        }

        /* Form Card */
        .auth-form-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.92));
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(28px);
            -webkit-backdrop-filter: blur(28px);
            border-radius: 24px;
            padding: 34px 32px;
            box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.7), 0 0 30px rgba(99, 102, 241, 0.1);
            position: relative;
        }

        .auth-form-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #ec4899, #8b5cf6, #3b82f6);
            border-top-left-radius: 24px;
            border-top-right-radius: 24px;
        }

        .auth-header {
            margin-bottom: 20px;
        }

        .auth-header h3 {
            margin: 0;
            font-size: 1.55rem;
            font-weight: 700;
            color: #ffffff;
        }

        .auth-header p {
            margin: 6px 0 0 0;
            font-size: 0.88rem;
            color: #94a3b8;
        }

        .demo-quick-banner {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.12));
            border: 1px solid rgba(99, 102, 241, 0.25);
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .demo-quick-banner span {
            font-size: 0.85rem;
            color: #c7d2fe;
            font-weight: 500;
        }

        /* Custom Streamlit button glow */
        div[data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%) !important;
            color: white !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.65rem 1.4rem !important;
            box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.5) !important;
            transition: all 0.25s ease !important;
            letter-spacing: 0.02em;
        }

        div[data-testid="stButton"] > button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 15px 30px -5px rgba(139, 92, 246, 0.6) !important;
            filter: brightness(1.1) !important;
        }

        div[data-testid="stButton"] > button[kind="secondary"] {
            background: rgba(30, 41, 59, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            color: #e2e8f0 !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
        }

        div[data-testid="stButton"] > button[kind="secondary"]:hover {
            background: rgba(51, 65, 85, 0.9) !important;
            border-color: rgba(99, 102, 241, 0.4) !important;
            color: #ffffff !important;
        }

        /* Input styling */
        .stTextInput > div > div > input {
            background-color: rgba(15, 23, 42, 0.75) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            color: #f8fafc !important;
            border-radius: 10px !important;
            font-size: 0.95rem !important;
        }

        .stTextInput > div > div > input:focus {
            border-color: #818cf8 !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25) !important;
        }

        /* Clean tab styling */
        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(15, 23, 42, 0.6);
            padding: 6px;
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            margin-bottom: 1.2rem;
        }

        [data-testid="stTabs"] [data-baseweb="tab"] {
            border-radius: 10px !important;
            padding: 8px 18px !important;
            font-weight: 600 !important;
            color: #94a3b8 !important;
            border: none !important;
            background: transparent !important;
        }

        [data-testid="stTabs"] [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(139, 92, 246, 0.25)) !important;
            color: #ffffff !important;
            border: 1px solid rgba(99, 102, 241, 0.4) !important;
        }

        [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_login_page():
    """Render the full professional login and registration interface."""
    inject_login_styles()

    left_hero, right_auth = st.columns([1.1, 0.9], gap="large")

    with left_hero:
        st.html(
            """
            <div class="auth-hero-card">
                <div class="brand-badge">&#10022; Advanced Sign Studio 2.0</div>
                <h1 class="brand-title">Smart Sign Language Detection &amp; Private Studio</h1>
                <p class="brand-subtitle">
                    Experience deep-learning gesture recognition with complete data isolation.
                    Every hand gesture sample, custom vocabulary class, and neural model is securely stored in your personal vault.
                </p>
                <div class="feature-grid">
                    <div class="feature-item">
                        <div class="feature-icon-box">&#128274;</div>
                        <div class="feature-text">
                            <h4>Zero Data Contamination</h4>
                            <p>Personal dataset storage guarantees your custom signs and training data are strictly accessible only by you.</p>
                        </div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon-box">&#9889;</div>
                        <div class="feature-text">
                            <h4>3D Hand Landmark Tracking</h4>
                            <p>High-precision MediaPipe tracking captures 21 spatial hand keypoints in real time via live webcam or upload.</p>
                        </div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon-box">&#129504;</div>
                        <div class="feature-text">
                            <h4>Few-Shot kNN &amp; Ensemble AI</h4>
                            <p>Bootstrap predictions without initial data, or train your own high-accuracy RandomForest ensemble classifier.</p>
                        </div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon-box">&#128483;</div>
                        <div class="feature-text">
                            <h4>Temporal Gating &amp; Voice Engine</h4>
                            <p>Smart trend-locking suppresses jitter, while natural speech synthesis converts recognized signs into spoken words.</p>
                        </div>
                    </div>
                </div>
                <div class="status-pill">
                    <div class="status-dot"></div>
                    <span>System Active &bull; Isolated Storage Ready &bull; Webcam Live</span>
                </div>
            </div>
            """
        )

    with right_auth:
        st.markdown(
            """
            <div class="auth-form-card">
                <div class="auth-header">
                    <h3>Studio Portal</h3>
                    <p>Sign in to access your personal workspace or register a new profile.</p>
                </div>
            """,
            unsafe_allow_html=True,
        )

        # Tab navigation for Sign In vs Register
        tab_signin, tab_register = st.tabs(["🔑 Sign In", "✨ Create Account"])

        with tab_signin:
            # Quick 1-click demo button
            st.markdown(
                """
                <div class="demo-quick-banner">
                    <span>💡 Instant Test: Click below for demo access without typing</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("⚡ Quick 1-Click Demo Login", key="quick_demo_login_btn", type="secondary", width="stretch"):
                # Ensure demo user exists
                auth_manager.load_users()
                success, msg, safe_user = auth_manager.authenticate_user("demo", "demo123")
                if success and safe_user:
                    st.session_state["authenticated_user"] = safe_user["username"]
                    st.session_state["user_info"] = safe_user
                    # Ensure demo db is initialized
                    user_data_manager.load_user_db("demo", seed_if_empty=True)
                    st.success("Signed in as Demo Explorer! Launching Studio...")
                    st.rerun()

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.8rem; margin: 8px 0;'>— OR ENTER YOUR CREDENTIALS —</p>", unsafe_allow_html=True)

            with st.form("signin_form", clear_on_submit=False):
                username_or_email = st.text_input(
                    "Username or Email",
                    placeholder="e.g. demo or your_email@example.com",
                    key="login_user_input",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="login_pwd_input",
                )
                remember_me = st.checkbox("Keep me signed in on this device", value=True)

                submit_login = st.form_submit_button(
                    "🚀 Sign In to Studio",
                    type="primary",
                    width="stretch",
                )

                if submit_login:
                    if not username_or_email or not password:
                        st.error("Please enter both username/email and password.")
                    else:
                        success, message, safe_user = auth_manager.authenticate_user(
                            username_or_email, password
                        )
                        if success and safe_user:
                            st.session_state["authenticated_user"] = safe_user["username"]
                            st.session_state["user_info"] = safe_user
                            # Ensure personal database is loaded/ready
                            user_data_manager.load_user_db(safe_user["username"], seed_if_empty=False)
                            st.success(f"{message} Loading your private workspace...")
                            st.rerun()
                        else:
                            st.error(message)

            st.caption("Default Demo account: `username: demo` | `password: demo123`")

        with tab_register:
            st.markdown(
                "<p style='color: #94a3b8; font-size: 0.88rem; margin-bottom: 12px;'>"
                "Create your personal sign language workspace. All gesture data you collect will be saved exclusively under your account."
                "</p>",
                unsafe_allow_html=True,
            )

            with st.form("register_form", clear_on_submit=False):
                reg_name = st.text_input("Full Name / Display Name", placeholder="e.g. Maya Chen", key="reg_name")
                reg_username = st.text_input(
                    "Desired Username",
                    placeholder="e.g. mayachen (3-24 characters, letters/numbers)",
                    key="reg_username",
                )
                reg_email = st.text_input("Email Address", placeholder="e.g. maya@example.com", key="reg_email")
                reg_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="At least 6 characters",
                    key="reg_password",
                )

                avatar_col1, avatar_col2 = st.columns([1, 2])
                with avatar_col1:
                    avatar_choice = st.selectbox(
                        "Avatar Badge",
                        ["🧑‍💻", "🚀", "🌟", "🦾", "⚡", "🎯", "🤖", "💎"],
                        index=0,
                    )
                with avatar_col2:
                    st.write("")
                    st.caption("Pick an avatar badge for your profile.")

                seed_starter = st.checkbox(
                    "Pre-load starter number dataset (0-9) so I can start predicting immediately",
                    value=True,
                    help="Copies the standard 0-9 digit landmark embeddings into your private storage. You can add, edit, or delete them anytime.",
                )

                submit_reg = st.form_submit_button(
                    "✨ Create Account & Launch Studio",
                    type="primary",
                    width="stretch",
                )

                if submit_reg:
                    success, message, new_user = auth_manager.register_user(
                        username=reg_username,
                        display_name=reg_name,
                        email=reg_email,
                        password=reg_password,
                        avatar=avatar_choice,
                    )
                    if success and new_user:
                        uname = new_user["username"]
                        # Initialize personal database
                        if seed_starter:
                            user_data_manager.seed_user_db_from_global(uname)
                        else:
                            user_data_manager.save_user_db(uname, {})

                        st.session_state["authenticated_user"] = uname
                        st.session_state["user_info"] = new_user
                        st.success(f"{message} Initializing your private workspace...")
                        st.rerun()
                    else:
                        st.error(message)

        st.markdown("</div>", unsafe_allow_html=True)
