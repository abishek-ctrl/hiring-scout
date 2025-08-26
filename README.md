# Hiring Scout

A Streamlit-based chatbot application designed to automate the initial screening process for technical candidates.

## Application Architecture

The application is structured into several directories to separate concerns:

*   **`app.py`**: The main entry point, which uses Streamlit to create the user interface and manage the application's state.
*   **`core/`**: Handles the logic for language model interactions and contains the prompt definitions.
*   **`ui/`**: Responsible for the visual styling and custom components of the chat interface.
*   **`utils/`**: Contains helper functions for database operations and input validation.

Data persistence is managed through a **MongoDB** database, which stores user sessions, chat messages, and final evaluations.

## Getting Started

### Prerequisites

*   Python 3.10+
*   A Groq Cloud API key
*   A MongoDB connection string

### Local Installation

1.  Clone the repository to your local machine.
    ```bash
    git clone <your-repo-url>
    cd hiring-scout
    ```

2.  Install the required Python dependencies.
    ```bash
    pip install -r requirements.txt
    ```

3.  Set up your environment variables. Create a `.env` file in the root directory and add your credentials:
    ```ini
    GROQ_API_KEY=your_groq_api_key_here
    GROQ_MODEL_NAME=model_name_here (e.g., mixtral-8x7b-32768)
    MONGO_CONNECTION_STRING=your_mongodb_connection_string_here
    ```

4.  Launch the application.
    ```bash
    streamlit run app.py
    ```

### Live Deployment

The application is deployed on Streamlit Cloud and can be accessed here:  
👉 **[https://hiring-scout.streamlit.app/](https://hiring-scout.streamlit.app/)**

## How It Works

1.  **Initiation**: Candidates begin by accepting a privacy notice and submitting their basic contact information (name, email, phone number).
2.  **Screening**: The chatbot initiates a conversation, following a strict script to gather essential information:
    *   Years of experience
    *   Desired positions
    *   Current location
    *   Technical skills (tech stack)
3.  **Technical Assessment**: After the initial info is collected, the chatbot asks 3-5 technical questions tailored to the candidate's stated tech stack.
4.  **Conclusion & Evaluation**: The conversation concludes, the system generates a final evaluation, and all data is stored.
5.  **Data Management**: Users have the option to manage their data and can delete all their information from the database at any time.

## Prompt Engineering

The chatbot's behavior is governed by two meticulously designed prompts:

1.  **Screening Prompt**: Instructs the LLM to act as a neutral hiring assistant. It enforces a strict sequence of questions, a non-evaluative tone, and defines separate flows for new and returning users. A unique `<thatsit>` marker signals the end of the conversation to the application logic.

2.  **Evaluation Prompt**: Used after the screening concludes. It structures the entire chat transcript into a detailed JSON object, extracting key details, generating a summary, listing strengths/weaknesses, and assigning a qualification score for the recruitment team.

## Development Challenges & Solutions

*   **Strict Conversation Flow**: Ensuring the LLM didn't deviate from the script was achieved by creating a highly specific system prompt with explicit "Guiding Principles" that enforce the question sequence and interaction style.
*   **Conversation End Signal**: The application detects the unique `<thatsit>` marker appended to the chatbot's final message to automatically trigger the evaluation and finalization processes.
*   **User Privacy ("Right to be Forgotten")**: A data management feature was implemented, allowing users to permanently delete their entire conversation history and personal details from the database, which required careful handling of related data across collections.

## Deployment

The application is deployed on **Streamlit Cloud**, which provides a simple and efficient platform for hosting Streamlit apps. The live version is always up to date with the `main` branch of this repository.

**Live App**: [https://hiring-scout.streamlit.app/](https://hiring-scout.streamlit.app/)