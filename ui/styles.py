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
    .chat-bubble {
        padding: 12px 16px;
        border-radius: 16px;
        margin: 8px 0;
        max-width: 50%;  /* limit bubble width */
        min-width: 120px; /* ensures small messages still look like bubbles */
        word-wrap: break-word;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        display: inline-block;
    }
    .user-msg {
        background-color: #2563eb;
        color: white;
        margin-left: auto;
        text-align: right;
    }
    .assistant-msg {
        background-color: #e5e7eb;
        color: #111827;
        margin-right: auto;
        text-align: left;
    }
    .title-container {
        text-align: center;
        padding: 20px;
    }
    .erase-btn {
        margin-top: 10px;
        font-size: 14px;
    }

    /* Modal styling */
    .modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.4);
        backdrop-filter: blur(4px);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    .modal-content {
        background: white;
        padding: 30px;
        border-radius: 12px;
        max-width: 600px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .modal h2 {
        margin-bottom: 16px;
    }
    .modal p {
        font-size: 15px;
        margin-bottom: 20px;
        color: #374151;
        text-align: left;
    }
    .modal button {
        margin: 0 10px;
        padding: 10px 18px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 15px;
    }
    .modal .accept {
        background-color: #2563eb;
        color: white;
    }
    .modal .decline {
        background-color: #e5e7eb;
        color: #111827;
    }
    </style>
    """
