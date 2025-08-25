import streamlit as st
from core.llm import GeminiChatClient
from core.prompts import SYSTEM_PROMPT
from ui.styles import load_css
from ui.components import render_message
from utils.storage import (
    init_db,
    create_session,
    get_session,
    set_privacy_accepted,
    load_messages,
    save_message,
    clear_session,
)

st.set_page_config(page_title="Hiring-Scout", page_icon="🤖", layout="wide")

# Setup
st.markdown(load_css(), unsafe_allow_html=True)
init_db()

# Session Handling
session_id_from_url = None
try:
    session_id_from_url = int(st.query_params.get("session_id"))
except (TypeError, ValueError):
    pass

if "session_id" not in st.session_state:
    if session_id_from_url:
        st.session_state.session_id = session_id_from_url
    else:
        new_session_id = create_session()
        st.session_state.session_id = new_session_id
        st.query_params["session_id"] = str(new_session_id)

    st.session_state.messages = load_messages(st.session_state.session_id)
    st.session_state.chat_active = True
    st.session_state.gemini_chat_client = GeminiChatClient(system_instruction=SYSTEM_PROMPT)

session = get_session(st.session_state.session_id)

# Privacy Notice
if session and not session["privacy_accepted"]:
    with st.container(border=True):
        st.markdown("## Privacy Notice")
        st.info(
            """
            Welcome to Hiring-Scout. We collect candidate details (such as name, contact information, experience, and technical background) strictly for recruitment and evaluation purposes. Your data will be stored securely in compliance with GDPR standards. You have the right to request deletion of your data at any time.

            **By clicking Accept, you consent to this data collection.**
            """
        )
        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if st.button("Accept", use_container_width=True, type="primary"):
                set_privacy_accepted(st.session_state.session_id, True)
                st.rerun()
        with col2:
            if st.button("Decline", use_container_width=True):
                st.warning("You must accept the privacy agreement to continue.")
                st.stop()
    st.stop()

# Data Management Dialog
if "show_data_dialog" not in st.session_state:
    st.session_state.show_data_dialog = False

_, col_btn = st.columns([0.8, 0.2])
with col_btn:
    if st.button("⚙️ Manage My Data", use_container_width=True):
        st.session_state.show_data_dialog = True

if st.session_state.show_data_dialog:
    @st.dialog("Manage Your Data")
    def manage_data_dialog():
        st.warning("⚠️ This action is irreversible.")
        st.write("Clicking 'Delete' will permanently erase all messages from this session from our database.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Delete My Data", type="primary", use_container_width=True):
                clear_session(st.session_state.session_id)
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_data_dialog = False
                st.rerun()
    manage_data_dialog()

# Title section
st.markdown(
    '<div class="title-container"><h1>🤖 Hiring-Scout</h1><p>Your AI-powered assistant for candidate screening</p></div>',
    unsafe_allow_html=True,
)

# Chat UI
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] in ["user", "assistant"]:
        render_message(msg["role"], msg["content"])
st.markdown("</div>", unsafe_allow_html=True)

# --- REVISED CHAT INPUT LOGIC ---
# The chat input is now controlled by `st.session_state.chat_active`
if st.session_state.get("chat_active", True):
    user_input = st.chat_input("Type your response...")
    if user_input:
        # Save and render user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        save_message(st.session_state.session_id, "user", user_input)
        render_message("user", user_input)

        # Get assistant response
        with st.spinner("Thinking..."):
            response = st.session_state.gemini_chat_client.send_message(user_input)
        
        # Check for the end-of-chat marker
        if response.strip().endswith("{thatsit}"):
            # Clean the response by removing the marker
            clean_response = response.strip().replace("{thatsit}", "")
            # The chat is no longer active
            st.session_state.chat_active = False
            # Use the cleaned response
            response_to_show = clean_response
        else:
            response_to_show = response

        # Save and render the assistant's (potentially cleaned) message
        st.session_state.messages.append({"role": "assistant", "content": response_to_show})
        save_message(st.session_state.session_id, "assistant", response_to_show)
        render_message("assistant", response_to_show)

        # If chat is no longer active, show a final message and rerun
        if not st.session_state.chat_active:
            st.info("This chat session has ended. Thank you for your time.")
            st.rerun()