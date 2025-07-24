#!/usr/bin/env python3
"""
SolidWorks Agent Streamlit UI
Pure UI layer - no business logic
"""

import streamlit as st
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from agent import SolidWorksAgentCore
from dtx_helper import DtxHelper
import asyncio

# Global DTX helper instance to reuse tokens
try:
    dtx_helper = DtxHelper()
except Exception:
    dtx_helper = None


def initialize_session_state():
    """Initialize Streamlit session state"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "current_session_data" not in st.session_state:
        st.session_state.current_session_data = None
    
    if "feedback_submitting" not in st.session_state:
        st.session_state.feedback_submitting = False
    
    if "feedback_success" not in st.session_state:
        st.session_state.feedback_success = False


def get_api_key() -> Optional[str]:
    """Get API key from environment only"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    return api_key


def create_agent() -> Optional[SolidWorksAgentCore]:
    """Create a stateless agent instance"""
    api_key = get_api_key()
    
    if not api_key:
        return None
    
    try:
        agent = SolidWorksAgentCore(api_key)
        
        # Restore current session from session state
        if ("current_session_data" in st.session_state and 
            st.session_state.current_session_data is not None):
            agent.sessions[st.session_state.session_id] = st.session_state.current_session_data
        
        return agent
    except Exception as e:
        return None


def save_agent_sessions(agent: SolidWorksAgentCore):
    """Save current agent session to Streamlit session state"""
    if st.session_state.session_id in agent.sessions:
        st.session_state.current_session_data = agent.sessions[st.session_state.session_id]


@st.dialog("💬 Give Feedback")
def feedback_modal():
    """Render feedback modal with form"""
    st.write("We'd love to hear your feedback about the SolidWorks Support Agent!")
    
    with st.form("feedback_form"):
        email = st.text_input("Email *", placeholder="your.email@company.com")
        positives = st.text_area("What did you like? *", placeholder="Tell us what worked well...")
        improvements = st.text_area("What could be improved? *", placeholder="Tell us what could be better...")
        
        submitted = st.form_submit_button("Submit Feedback", use_container_width=True, disabled=st.session_state.feedback_submitting)
        
        if submitted and not st.session_state.feedback_submitting:
            # Validate all fields are filled
            if not email.strip():
                st.error("Email is required.")
                return
            if not positives.strip():
                st.error("Please tell us what you liked.")
                return
            if not improvements.strip():
                st.error("Please tell us what could be improved.")
                return
                
            # Set submitting state to prevent double-click
            st.session_state.feedback_submitting = True
            
            try:
                # Check if DTX helper is available
                if dtx_helper is None:
                    st.error("❌ DTX service is not configured. Please check environment variables.")
                    st.info("Required: DTX_BASE_URL, DTX_LOGIN_EMAIL, DTX_LOGIN_PASSWORD, DTX_TENANT_ID")
                    st.session_state.feedback_submitting = False
                    return
                
                # Submit feedback using global DTX helper
                with st.spinner("Submitting feedback..."):
                    result = asyncio.run(dtx_helper.create_feedback_form(email, positives, improvements))
                
                # Set success state and trigger modal close
                st.session_state.feedback_success = True
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Sorry, there was an error submitting your feedback: {str(e)}")
                st.info("Please try again later or contact support directly.")
            finally:
                # Reset submitting state
                st.session_state.feedback_submitting = False


def render_api_key_missing():
    """Render API key missing message"""
    st.error("🔑 **Perplexity API Key Required**")
    
    st.markdown("""
    ### Setup Required
    
    The SolidWorks Support Agent requires a Perplexity API key to function.
    
    **To setup:**
    
    1. Get your API key from [Perplexity API Settings](https://www.perplexity.ai/settings/api)
    
    2. Add it to your environment:
    
    **Option A: .env file (Recommended)**
    ```bash
    # Create or edit .env file
    PERPLEXITY_API_KEY=your_api_key_here
    ```
    
    **Option B: Environment variable**
    ```bash
    export PERPLEXITY_API_KEY=your_api_key_here
    ```
    
    3. Restart the application
    
    ---
    
    **Note:** For security reasons, API keys cannot be entered through the web interface.
    """)


def render_sidebar(agent: SolidWorksAgentCore):
    """Render sidebar with controls and session info"""
    st.sidebar.title("🔧 SolidWorks Agent")
    
    # Connection status
    st.sidebar.success("✅ Connected")
    
    # Model selection
    st.sidebar.subheader("⚙️ Settings")
    current_model = agent.get_current_model()
    available_models = agent.get_available_models()
    
    selected_model = st.sidebar.selectbox(
        "Model",
        available_models,
        index=available_models.index(current_model) if current_model in available_models else 0,
        key="model_selector"
    )
    
    if selected_model != current_model:
        if agent.switch_model(selected_model):
            st.sidebar.success(f"🔄 Switched to {selected_model}")
            st.rerun()
    
    # Session info
    session = agent.get_session(st.session_state.session_id)
    if session:
        st.sidebar.subheader("📊 Session Info")
        summary = agent.get_session_summary(st.session_state.session_id)
        if summary:
            st.sidebar.metric("Questions Asked", summary["user_questions"])
            st.sidebar.metric("Total Messages", summary["message_count"])
            st.sidebar.text(f"Duration: {summary['session_duration']}")
    
    # Session controls
    st.sidebar.subheader("🛠️ Actions")
    
    if st.sidebar.button("🔄 Reset Chat", help="Clear conversation and start fresh", use_container_width=True):
        # Clear both Streamlit chat history and agent session
        if "messages" in st.session_state:
            st.session_state.messages = []
        agent.clear_session(st.session_state.session_id)
        save_agent_sessions(agent)
        st.rerun()
    
    if st.sidebar.button("💬 Give Feedback", help="Share your feedback with us", use_container_width=True):
        feedback_modal()
    
    # Show success message after feedback submission
    if st.session_state.feedback_success:
        st.sidebar.success("✅ Thank you for your feedback!")
        st.session_state.feedback_success = False
    
    # Help section
    with st.sidebar.expander("❓ Help", expanded=False):
        st.markdown("""
        **What I can help with:**
        - 🔧 SolidWorks troubleshooting
        - 🎯 Modeling techniques
        - 📐 Assembly & drawings
        - 🧪 Simulation workflows
        - ⚙️ Configuration management
        
        **Tips:**
        - Be specific about SolidWorks version
        - Include error messages
        - Describe exact steps
        """)


def render_message(message, is_user: bool = True):
    """Render a single message"""
    if is_user:
        with st.chat_message("user"):
            st.markdown(message.content)
    else:
        with st.chat_message("assistant"):
            st.markdown(message.content)
            
            # Show metadata for assistant messages
            if hasattr(message, 'metadata') and message.metadata:
                with st.expander("ℹ️ Response Details", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col3:
                        if "processing_time_ms" in message.metadata:
                            time_ms = message.metadata["processing_time_ms"]
                            st.metric("Response Time", f"{time_ms}ms")


def render_chat_interface(agent: SolidWorksAgentCore):
    """Render main chat interface following Streamlit's official pattern"""
    
    # Initialize chat history in session state (Streamlit's recommended approach)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # React to user input
    if prompt := st.chat_input("Ask me anything about SolidWorks..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching SolidWorks knowledge..."):
                try:
                    response, _ = agent.process_message(st.session_state.session_id, prompt)
                    
                    # Display response
                    st.markdown(response.content)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response.content})
                    
                    # Save agent sessions
                    save_agent_sessions(agent)
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})


def render_welcome_message():
    """Render welcome message for new users"""
    st.markdown("""
    # 🔧 SolidWorks Support Agent
    
    **Powered by Perplexity API with real-time SolidWorks knowledge**
    
    I'm your specialized SolidWorks technical expert. I can help with:
    
    - 🔧 **Troubleshooting**: Crashes, errors, performance issues
    - 🎯 **Modeling**: 3D techniques, best practices, workflows  
    - 📐 **Assemblies**: Large assembly management, configurations
    - 🧪 **Simulation**: Analysis setup, mesh settings, results
    - ⚙️ **Configuration**: PDM, toolbox, system optimization
    
    ## 💡 Tips for Best Results:
    - **Be specific** about your SolidWorks version
    - **Include exact error messages** when reporting issues
    - **Describe the steps** that lead to problems
    - **Mention system specs** for performance issues
    
    ## 🚨 Important:
    - I **only answer SolidWorks-related questions**
    - All responses include **source links** for verification
    - If your question lacks context, I'll ask for **more details** first
    
    ---
    
    **Ready to help! Ask me anything about SolidWorks below. 👇**
    """)


def main():
    """Main Streamlit app following official Streamlit chat pattern"""
    st.set_page_config(
        page_title="SolidWorks Support Agent",
        page_icon="🔧",
        layout="wide"
    )
    
    st.title("🔧 SolidWorks Support Agent")
    
    # Initialize session
    initialize_session_state()
    
    # Create agent
    agent = create_agent()
    
    if not agent:
        render_api_key_missing()
        return
    
    # Render sidebar
    render_sidebar(agent)
    
    # Show welcome message if no chat history
    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        st.markdown("""
        **I'm your SolidWorks technical expert!** I can help with:
        
        - 🔧 **Troubleshooting**: Crashes, errors, performance issues
        - 🎯 **Modeling**: 3D techniques, workflows, best practices
        - 📐 **Assemblies**: Large assembly management, configurations  
        - 🧪 **Simulation**: Analysis setup, mesh settings, results
        - ⚙️ **Configuration**: PDM, toolbox, system optimization
        
        **Ask me anything about SolidWorks below! 👇**
        """)
    
    # Render chat interface
    render_chat_interface(agent)


if __name__ == "__main__":
    main()