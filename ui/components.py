import streamlit as st

def render_message(role, content):
    """Render a single chat message aligned by role using a flexbox container."""
    row_class = "user-row" if role == "user" else "assistant-row"
    bubble_class = "user-msg" if role == "user" else "assistant-msg"
    
    # Wrap the bubble in a flex container row
    st.markdown(
        f'''
        <div class="message-row {row_class}">
            <div class="chat-bubble {bubble_class}">
                {content}
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )