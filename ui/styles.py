def load_css():
    """Return custom CSS for chat layout with proper bubble sizing and modal popup."""
    return """
    <style>
    body {
        background-color: #f9fafb;
    }
    .chat-container {
        max-width: 800px;
        margin: auto;
        padding: 20px;
    }
    /* New styles for alignment */
    .message-row {
        display: flex;
        margin-bottom: 10px;
    }
    .user-row {
        justify-content: flex-end; /* Aligns bubble to the right */
    }
    .assistant-row {
        justify-content: flex-start; /* Aligns bubble to the left */
    }
    /* Updated bubble style */
    .chat-bubble {
        padding: 12px 16px;
        border-radius: 16px;
        max-width: 70%; /* Bubbles can be a bit wider */
        word-wrap: break-word;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: left; /* Ensure text is left-aligned within the bubble */
    }
    .user-msg {
        background-color: #2563eb;
        color: white;
    }
    .assistant-msg {
        background-color: #e5e7eb;
        color: #111827;
    }
    .title-container {
        text-align: center;
        padding: 20px;
    }
    /* (The rest of your CSS for modal, etc., can remain the same) */
    </style>
    """