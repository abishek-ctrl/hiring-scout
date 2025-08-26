import streamlit as st
from core.llm import GroqChatClient
from core.prompts import SYSTEM_PROMPT, EVALUATION_PROMPT
from ui.styles import load_css
from ui.components import render_message
from utils.storage import (
    get_or_create_user_session,
    load_messages,
    save_message,
    save_evaluation,
)
from utils.validators import validate_email, validate_phone

st.set_page_config(page_title="Hiring-Scout", page_icon="🤖", layout="wide")
st.markdown(load_css(), unsafe_allow_html=True)

# --- PHASE 1: INITIALIZE SESSION STATE & PRIVACY NOTICE ---
if "user_details_submitted" not in st.session_state:
    st.session_state.user_details_submitted = False
    st.session_state.privacy_accepted = False

if not st.session_state.privacy_accepted:
    with st.container(border=True):
        st.markdown("## Privacy Notice")
        st.info(
            """
            Welcome to Hiring-Scout. We collect candidate details (such as name, contact information, experience, and technical background) strictly for recruitment and evaluation purposes. Your data will be stored securely.

            **By clicking Accept, you consent to this data collection.**
            """
        )
        if st.button("Accept", type="primary"):
            st.session_state.privacy_accepted = True
            st.rerun()
    st.stop()

# --- PHASE 2: USER DETAILS FORM ---
if st.session_state.privacy_accepted and not st.session_state.user_details_submitted:
    st.markdown("### Please provide your details to begin")
    with st.form(key="user_details_form"):
        name = st.text_input("Full Name", key="user_name_input")
        email = st.text_input("Email Address", key="user_email_input")
        phone = st.text_input("Phone Number", key="user_phone_input")
        submit_button = st.form_submit_button(label="Start Screening")

        if submit_button:
            if name and validate_email(email) and validate_phone(phone):
                with st.spinner("Setting up your session..."):
                    session_id, is_new_user = get_or_create_user_session(name, email, phone)
                    
                    st.session_state.session_id = session_id
                    st.session_state.is_new_user = is_new_user
                    st.session_state.user_name = name # Save name for greeting
                    st.session_state.user_details_submitted = True
                    st.rerun()
            else:
                st.error("Please fill out all fields with valid information.")
    st.stop()

# --- PHASE 3: CHAT INTERFACE ---
if st.session_state.user_details_submitted:
    # Initialize chat client and messages ONCE
    if "messages" not in st.session_state:
        st.session_state.messages = load_messages(st.session_state.session_id)
        
        if st.session_state.is_new_user and not st.session_state.messages:
            # For a brand new user, create the first message
            user_name = st.session_state.user_name
            welcome_message = f"Hello {user_name}, and thank you for your interest. To begin, how many years of professional experience do you have?"
            st.session_state.messages.append({"role": "assistant", "content": welcome_message})
            save_message(st.session_state.session_id, "assistant", welcome_message)

        st.session_state.groq_chat_client = GroqChatClient(
            system_instruction=SYSTEM_PROMPT,
            history=st.session_state.messages
        )

    # Render Title and Chat History
    st.markdown('<div class="title-container"><h1>🤖 Hiring-Scout</h1></div>', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        render_message(msg["role"], msg["content"])

    # Chat input logic
    user_input = st.chat_input("Type your response...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        save_message(st.session_state.session_id, "user", user_input)
        
        with st.spinner("Thinking..."):
            response = st.session_state.groq_chat_client.send_message(user_input)
        
        response_to_show = response
        
        if response.strip().endswith("{thatsit}"):
            response_to_show = response.strip().replace("{thatsit}", "")
            st.session_state.evaluation_done = True
            
            with st.spinner("Finalizing evaluation..."):
                evaluation = st.session_state.groq_chat_client.generate_evaluation(st.session_state.messages)
                if evaluation:
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
        
        st.session_state.messages.append({"role": "assistant", "content": response_to_show})
        save_message(st.session_state.session_id, "assistant", response_to_show)
        
        st.rerun()