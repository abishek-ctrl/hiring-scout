import streamlit as st

def render_message(role, content):
    """Render a single chat message aligned by role."""
    css_class = "user-msg" if role == "user" else "assistant-msg"
    st.markdown(f'<div class="chat-bubble {css_class}">{content}</div>', unsafe_allow_html=True)
