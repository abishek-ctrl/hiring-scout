import os
import google.genai as genai
# from dotenv import load_dotenv

# load_dotenv()

class GeminiChatClient:
    """
    A class to handle stateful chat sessions with the Gemini API.
    """
    def __init__(self, model_name="gemini-2.5-flash-lite", system_instruction=None, history=None):
        """
        Initializes the chat session.

        Args:
            model_name (str): The name of the Gemini model to use.
            system_instruction (str, optional): A system prompt to guide the model.
            history (list, optional): A list of previous messages to load into the chat context.
        """
        self.client = genai.Client()
        
        initial_history = []
        # Start with the system instruction if provided
        if system_instruction:
            initial_history.extend([
                {'role': 'user', 'parts': [{'text': system_instruction}]},
                {'role': 'model', 'parts': [{'text': "Understood. I'm ready to assist."}]}
            ])

        # Append the conversation history if provided, converting to the required format
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

        Args:
            message (str): The user's new message.

        Returns:
            str: The assistant's text reply.
        """
        response = self.chat.send_message(message)
        return response.text
        
    def generate_evaluation(self, chat_history: list) -> dict:
        """
        Generates a structured evaluation of the candidate based on the chat history.

        Args:
            chat_history (list): A list of message dictionaries from the conversation.

        Returns:
            dict: A dictionary containing the parsed evaluation (summary, score, etc.).
        """
        # Format the chat history into a simple string transcript
        transcript = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])
        
        # Create the evaluation prompt
        prompt = EVALUATION_PROMPT.format(chat_history=transcript)
        
        # Use a non-chat generation method for this one-shot task
        model = self.client.models.get('models/gemini-pro') # Using gemini-pro for better JSON generation
        try:
            response = model.generate_content(prompt)
            # Clean up and parse the JSON from the model's response
            json_text = response.text.strip().lstrip("```json").rstrip("```")
            return json.loads(json_text)
        except Exception as e:
            print(f"Error generating or parsing evaluation: {e}")
            return None # Return None on failure