"""
Email validation and browser storage handler for Streamlit UI
"""
import re
import streamlit as st


def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def get_stored_email_js():
    """JavaScript code to get email from browser local storage"""
    js_code = """
    <script>
    function getStoredEmail() {
        return localStorage.getItem('solidworks_agent_email');
    }
    window.parent.postMessage({
        type: 'streamlit:getStoredEmail',
        email: getStoredEmail()
    }, '*');
    </script>
    """
    return js_code


def store_email_js(email: str):
    """JavaScript code to store email in browser local storage"""
    js_code = f"""
    <script>
    localStorage.setItem('solidworks_agent_email', '{email}');
    </script>
    """
    return js_code


def clear_email_js():
    """JavaScript code to clear email from browser local storage"""
    js_code = """
    <script>
    localStorage.removeItem('solidworks_agent_email');
    </script>
    """
    return js_code


def initialize_email_session():
    """Initialize email in session state"""
    if "user_email" not in st.session_state:
        st.session_state.user_email = None


def render_email_entry():
    """Render email entry form"""
    st.markdown("""
    # 🔧 SolidWorks Support Agent
    
    ### 📧 Email Required
    
    Please enter your email address to access the SolidWorks Support Agent.
    Your email will be stored locally in your browser for future sessions.
    """)
    
    with st.form("email_form", clear_on_submit=False):
        email = st.text_input(
            "Email Address",
            placeholder="your.name@company.com",
            help="This email will be stored locally in your browser"
        )
        
        submitted = st.form_submit_button("Continue to Agent", use_container_width=True)
        
        if submitted:
            if not email:
                st.error("❌ Please enter an email address")
            elif not is_valid_email(email):
                st.error("❌ Please enter a valid email address")
            else:
                # Store email in session state and local storage
                st.session_state.user_email = email
                
                # Use JavaScript to store in browser
                st.components.v1.html(store_email_js(email), height=0)
                
                st.success(f"✅ Welcome! Email saved: {email}")
                st.rerun()


def render_user_info_sidebar():
    """Render user email info in sidebar"""
    if st.session_state.user_email:
        st.sidebar.markdown("---")
        st.sidebar.subheader("👤 User Info")
        st.sidebar.text(f"📧 {st.session_state.user_email}")
        
        if st.sidebar.button("🔄 Change Email", help="Clear stored email and re-enter"):
            st.session_state.user_email = None
            # Clear from browser storage
            st.components.v1.html(clear_email_js(), height=0)
            st.rerun()


def get_user_email():
    """Get current user email from session state"""
    return st.session_state.get("user_email", None)


def is_email_provided():
    """Check if user email is provided"""
    return st.session_state.get("user_email") is not None