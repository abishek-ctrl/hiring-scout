import os
import json
from dotenv import load_dotenv
from groq import Groq
from .prompts import EVALUATION_PROMPT

# Load environment variables from the .env file
load_dotenv()

# Fetch credentials and configuration from environment variables
api_key = os.environ.get("GROQ_API_KEY")
model_name = os.environ.get("GROQ_MODEL_NAME")

# A robust check to ensure the app doesn't start without necessary secrets
if not api_key or not model_name:
    raise ValueError("GROQ_API_KEY and GROQ_MODEL_NAME must be set in your .env file.")

# Instantiate the main client that will be used by the class
client = Groq(api_key=api_key)


class GroqChatClient:
    """
    A class to handle stateful chat sessions with the Groq API.
    It reads the model name from the environment, so it doesn't need to be passed in.
    """
    def __init__(self, system_instruction=None, history=None):
        self.model = model_name
        self.history = []

        # Set the system prompt for the conversation
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
        self.history.append({"role": "user", "content": message})

        chat_completion = client.chat.completions.create(
            messages=self.history,
            model=self.model
        )
        response_content = chat_completion.choices[0].message.content

        # Maintain the state by adding the assistant's response to the history
        self.history.append({"role": "assistant", "content": response_content})

        return response_content
        
    def generate_evaluation(self, chat_history: list) -> dict:
        """
        Generates a structured evaluation using a one-off call to the API.
        """
        transcript = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])
        prompt = EVALUATION_PROMPT.format(chat_history=transcript)
        
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
            # This provides a more helpful error message in the terminal
            print(f"Error during evaluation: {e}")
            return None

    def summarize_history(self, chat_history: list) -> str:
        """
        Generates a concise summary of a past conversation.
        """
        transcript = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])
        
        summary_prompt = f"""
        Please provide a concise, one-paragraph summary of the key points 
        from the following candidate conversation transcript:
        ---
        {transcript}
        ---
        Focus on the candidate's stated experience, tech stack, and performance on technical questions.
        """
        
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": summary_prompt}],
                model=self.model,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error during history summarization: {e}")
            return "Could not summarize previous conversation."