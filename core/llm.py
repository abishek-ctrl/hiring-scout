import os
import json
import streamlit as st
import google.genai as genai
from .prompts import EVALUATION_PROMPT

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except (KeyError, AttributeError):
    st.error("GEMINI_API_KEY not found in Streamlit secrets. Please add it.")
    st.stop()

class GeminiChatClient:
    """
    A class to handle stateful chat sessions with the Gemini API.
    """
    def __init__(self, model_name="gemini-2.5-flash-lite", system_instruction=None, history=None):
        """
        Initializes the chat session.
        """
        self.client = genai.Client()
        
        initial_history = []
        if system_instruction:
            initial_history.extend([
                {'role': 'user', 'parts': [{'text': system_instruction}]},
                {'role': 'model', 'parts': [{'text': "Understood. I'm ready to assist."}]}
            ])

        if history:
            for message in history:
                role = 'model' if message['role'] == 'assistant' else 'user'
                initial_history.append({'role': role, 'parts': [{'text': message['content']}]})

        self.chat = self.client.chats.create(
            model=f'models/{model_name}',
            history=initial_history
        )

    def send_message(self, message: str) -> str:
        """
        Sends a message to the ongoing chat session.
        """
        response = self.chat.send_message(message)
        return response.text
        
    def generate_evaluation(self, chat_history: list) -> dict:
        """
        Generates a structured evaluation of the candidate based on the chat history.
        """
        transcript = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])
        prompt = EVALUATION_PROMPT.format(chat_history=transcript)
        
        model = self.client.models.get('models/gemini-2.5-flash-lite')
        try:
            response = model.generate_content(prompt)
            json_text = response.text.strip().lstrip("```json").rstrip("```")
            return json.loads(json_text)
        except Exception as e:
            print(f"Error generating or parsing evaluation: {e}")
            st.error("Failed to generate the final candidate evaluation.")
            return None