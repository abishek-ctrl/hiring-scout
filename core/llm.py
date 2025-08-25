# core/llm.py

import os
import google.genai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API key
class GeminiChatClient:
    """
    A class to handle stateful chat sessions with the Gemini API using genai.Client().
    """
    def __init__(self, model_name="gemini-2.5-flash-lite", system_instruction=None):
        """
        Initializes the chat session.

        Args:
            model_name (str): The name of the Gemini model to use.
            system_instruction (str, optional): A system prompt to guide the model.
        """
        self.client = genai.Client()
        self.chat = self.client.chats.create(
            model=f'models/{model_name}',
            # The system instruction is now part of the chat history
            history=[
                {'role': 'user', 'parts': [{'text': system_instruction}]},
                {'role': 'model', 'parts': [{'text': "Understood. I'm ready to assist."}]}
            ] if system_instruction else []
        )

    def send_message(self, message: str) -> str:
        """
        Sends a message to the ongoing chat session.

        Args:
            message (str): The user's new message.

        Returns:
            str: The assistant's text reply.
        """
        response = self.chat.send_message(message)
        return response.text