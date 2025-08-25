# core/state.py

import streamlit as st
from core.llm import GeminiChatClient
from core.prompts import SYSTEM_PROMPT # Your system prompt from another file

def init_state():
    """Initializes the Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "chat_active" not in st.session_state:
        st.session_state.chat_active = True

    # Initialize the Gemini chat client and store it in the session state
    if "gemini_chat_client" not in st.session_state:
        st.session_state.gemini_chat_client = GeminiChatClient(
            system_instruction=SYSTEM_PROMPT
        )