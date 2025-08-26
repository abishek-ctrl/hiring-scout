import streamlit as st
import json
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
    save_evaluation,
)

st.set_page_config(page_title="Hiring-Scout", page_icon="🤖", layout="wide")

# Setup
st.markdown(load_css(), unsafe_allow_html=True)
init_db()

session_id_from_url = None
try:
    session_id_from_url = int(st.query_params.get("session_id"))
except (TypeError, ValueError):
    pass

if "session_id" not in st.session_state:
    if session_id_from_url:
        st.session_state.session_id = session_id_from_url
        st.session_state.messages = load_messages(st.session_state.session_id)
    else:
        new_session_id = create_session()
        st.session_state.session_id = new_session_id
        st.query_params["session_id"] = str(new_session_id)
        
        welcome_message = "Hello there! I'm Hiring-Scout, your intelligent hiring assistant. To start, could you please share your full name so we can record your application?"
        save_message(new_session_id, "assistant", welcome_message)
        st.session_state.messages = [{"role": "assistant", "content": welcome_message}]
    
    st.session_state.chat_active = True
    st.session_state.gemini_chat_client = GeminiChatClient(
        system_instruction=SYSTEM_PROMPT,
        history=st.session_state.messages
    )

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
                # 1. Clear the old session data from the DB
                clear_session(st.session_state.session_id)
                
                # 2. Clear the session state in the browser
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                
                # 3. Create a fresh session and set the default message
                new_session_id = create_session()
                welcome_message = "Hello there! I'm Hiring-Scout, your intelligent hiring assistant. To start, could you please share your full name so we can record your application?"
                save_message(new_session_id, "assistant", welcome_message)
                
                # 4. Set the new session ID in the URL and rerun
                st.query_params["session_id"] = str(new_session_id)
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

if st.session_state.get("chat_active", True):
    user_input = st.chat_input("Type your response...")
    if user_input:
        # 1. Update state with user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        save_message(st.session_state.session_id, "user", user_input)

        # 2. Get assistant response
        with st.spinner("Thinking..."):
            response = st.session_state.gemini_chat_client.send_message(user_input)
        
        response_to_show = response
        
        # 3. Check for the end-of-chat marker
        if response.strip().endswith("{thatsit}"):
            response_to_show = response.strip().replace("{thatsit}", "")
            st.session_state.chat_active = False
        
        # 4. Update state with assistant response
        st.session_state.messages.append({"role": "assistant", "content": response_to_show})
        save_message(st.session_state.session_id, "assistant", response_to_show)

        if not st.session_state.chat_active:
            with st.spinner("Finalizing evaluation..."):
                evaluation = st.session_state.gemini_chat_client.generate_evaluation(st.session_state.messages)
                if evaluation:
                    # Save the new structured data
                    save_evaluation(
                        st.session_state.session_id,
                        evaluation.get("full_name", "N/A"),
                        evaluation.get("email", "N/A"),
                        evaluation.get("phone", "N/A"),
                        evaluation.get("summary"),
                        evaluation.get("strengths"),
                        evaluation.get("weaknesses"),
                        evaluation.get("score"),
                    )

        # 6. Rerun to display the new messages without rendering them twice
        st.rerun()

# This is shown when the chat is no longer active
if not st.session_state.get("chat_active", True):
    st.info("This chat session has ended. Thank you for your time.")

# --- SCRIPT TO PREVENT SCROLLING TO TOP ---
st.markdown('<div id="end-of-chat-anchor" style="height: 1px;"></div>', unsafe_allow_html=True)
js_code = """
<script>
    // Find the anchor element
    var anchor = document.getElementById("end-of-chat-anchor");
    // Scroll to the anchor
    if (anchor) {
        anchor.scrollIntoView({behavior: "auto", block: "end"});
    }
</script>
"""
st.components.v1.html(js_code, height=0)