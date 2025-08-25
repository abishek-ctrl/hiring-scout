import streamlit as st
from core.state import init_state
from ui.styles import load_css
from ui.components import render_message
from utils.storage import init_db, create_session, get_session, set_privacy_accepted, load_messages, save_message, clear_session

st.set_page_config(page_title="Hiring-Scout", page_icon="🤖", layout="wide")

# Setup
st.markdown(load_css(), unsafe_allow_html=True)
init_db()
init_state()

# Ensure session_id exists
if "session_id" not in st.session_state:
    st.session_state.session_id = create_session()

session = get_session(st.session_state.session_id)

if not session["privacy_accepted"]:
    st.markdown("## Privacy Notice")
    st.info(
        """
        Welcome to Hiring-Scout.  
        We collect candidate details (such as name, contact information, experience, and technical background) strictly for recruitment and evaluation purposes.  

        Your data will be stored securely in compliance with GDPR standards.  
        You have the right to request deletion of your data at any time.  

        By clicking **Accept**, you consent to this data collection.
        """
    )

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Accept", use_container_width=True):
            set_privacy_accepted(st.session_state.session_id, True)
            st.rerun()
    with col2:
        if st.button("Decline", use_container_width=True):
            st.warning("You declined the privacy agreement. Refresh to reconsider.")
    st.stop()


# Title section
st.markdown('<div class="title-container"><h1>🤖 Hiring-Scout</h1><p>Your AI-powered assistant for candidate screening</p></div>', unsafe_allow_html=True)

# GDPR erase
if st.button("Erase my data", key="erase", help="Delete all data from this session"):
    clear_session(st.session_state.session_id)
    st.success("Your data has been erased.")
    st.rerun()

# Load messages
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = load_messages(st.session_state.session_id)

# Chat UI
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] in ["user", "assistant"]:
        render_message(msg["role"], msg["content"])
st.markdown('</div>', unsafe_allow_html=True)

# Chat input
if st.session_state.chat_active:
    user_input = st.chat_input("Type your response...")
    if user_input:
        # Save user msg
        st.session_state.messages.append({"role": "user", "content": user_input})
        save_message(st.session_state.session_id, "user", user_input)
        render_message("user", user_input)

        # Gemini response
        with st.spinner("Thinking..."):
            response = st.session_state.gemini_chat_client.send_message(user_input)

        st.session_state.messages.append({"role": "assistant", "content": response})
        save_message(st.session_state.session_id, "assistant", response)
        render_message("assistant", response)

        # Exit check
        if any(word in user_input.lower() for word in ["quit", "exit", "bye", "thank you"]):
            st.session_state.chat_active = False
            st.info("Thank you for using Hiring-Scout. The chat has ended.")
            st.rerun()
