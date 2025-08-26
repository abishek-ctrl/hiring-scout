import os
import json
from dotenv import load_dotenv
from groq import Groq
from .prompts import SYSTEM_PROMPT, EVALUATION_PROMPT

# Load environment variables from the .env file
load_dotenv()

# --- Groq API Client Initialization ---
api_key = os.environ.get("GROQ_API_KEY")
model_name = os.environ.get("GROQ_MODEL_NAME")

if not api_key or not model_name:
    raise ValueError("GROQ_API_KEY and GROQ_MODEL_NAME must be set in your .env file.")

client = Groq(api_key=api_key)

class GroqChatClient:
    """
    A class to handle stateful chat sessions with the Groq API.
    """
    def __init__(self, system_instruction=None, history=None):
        self.model = model_name
        self.history = []
        if system_instruction:
            self.history.append({"role": "system", "content": system_instruction})
        if history:
            for message in history:
                self.history.append({"role": message["role"], "content": message["content"]})

    def send_message(self, message: str) -> str:
        """
        Sends a message by passing the entire history to the Groq API.
        """
        self.history.append({"role": "user", "content": message})
        chat_completion = client.chat.completions.create(
            messages=self.history,
            model=self.model
        )
        response_content = chat_completion.choices[0].message.content
        self.history.append({"role": "assistant", "content": response_content})
        return response_content
        
    def generate_evaluation(self, chat_history: list, full_name: str, email: str, phone: str) -> dict:
        """
        Generates a structured evaluation, providing user details for context.
        """
        transcript = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])
        
        # Format the prompt with all the necessary details
        prompt = EVALUATION_PROMPT.format(
            full_name=full_name,
            email=email,
            phone=phone,
            chat_history=transcript
        )
        
        try:
            evaluation_messages = [
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ]
            response = client.chat.completions.create(
                messages=evaluation_messages,
                model=self.model,
                response_format={"type": "json_object"},
            )
            json_text = response.choices[0].message.content
            return json.loads(json_text)
        except Exception as e:
            print(f"Error during evaluation: {e}")
            return None