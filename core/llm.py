import json
import streamlit as st
from groq import Groq
from .prompts import EVALUATION_PROMPT
from dotenv import load_dotenv
load_dotenv()

client = Groq()



class GroqChatClient:
    """
    A class to handle stateful chat sessions with the Groq API.
    """
    def __init__(self, model_name="qwen/qwen2-72b-instruct", system_instruction=None, history=None):
        """
        Initializes the chat session for the stateless Groq API.
        """
        self.model = model_name
        self.history = []

        # Set the system prompt
        if system_instruction:
            self.history.append({"role": "system", "content": system_instruction})

        # Load existing conversation history if provided
        if history:
            for message in history:
                self.history.append({"role": message["role"], "content": message["content"]})

    def send_message(self, message: str) -> str:
        """
        Sends a message by passing the entire history to the Groq API.
        """
        # Add the new user message to our history
        self.history.append({"role": "user", "content": message})

        # Make the API call
        chat_completion = client.chat.completions.create(
            messages=self.history,
            model=self.model,
            stream=False,
        )
        # Get the response
        response_content = chat_completion.choices[0].message.content

        # Add the assistant's response to our history
        self.history.append({"role": "assistant", "content": response_content})

        return response_content
        
    def generate_evaluation(self, chat_history: list) -> dict:
        """
        Generates a structured evaluation using a one-off call to the API.
        """
        transcript = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])
        prompt = EVALUATION_PROMPT.format(chat_history=transcript)
        
        try:
            # Create a messages list specifically for this one-time evaluation
            evaluation_messages = [
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ]

            response = client.chat.completions.create(
                messages=evaluation_messages,
                model=self.model,
                response_format={"type": "json_object"}, # Use JSON mode for reliability
                stream=False,
            )
            
            json_text = response.choices[0].message.content
            return json.loads(json_text)
            
        except Exception as e:
            print(f"Error generating or parsing evaluation: {e}")
            st.error("Failed to generate the final candidate evaluation.")
            return None
