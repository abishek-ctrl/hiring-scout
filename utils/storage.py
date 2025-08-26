import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId

def get_mongo_client():
    """Initializes connection to MongoDB Atlas."""
    # Get the connection string from Streamlit's secrets
    connection_string = st.secrets["MONGO_CONNECTION_STRING"]
    client = MongoClient(connection_string)
    return client

def init_db():
    """
    Verifies connection to the database and gets the collections.
    MongoDB creates collections automatically when you first add data.
    """
    client = get_mongo_client()
    db = client.hiring_scout_db # You can name your database anything
    # Add the new evaluations_collection
    return db.sessions, db.messages, db.evaluations

sessions_collection, messages_collection, evaluations_collection = init_db()

def create_session():
    """Create a new session and return its ID."""
    session_data = {"privacy_accepted": False}
    result = sessions_collection.insert_one(session_data)
    # Return the ID as a string, as Streamlit's URL params work best with strings
    return str(result.inserted_id)

def get_session(session_id):
    """Return session data by ID."""
    try:
        # Convert string ID back to ObjectId for querying
        oid = ObjectId(session_id)
        session = sessions_collection.find_one({"_id": oid})
        if session:
            # Add the 'id' field to be compatible with the old code
            session['id'] = str(session['_id'])
            return session
    except Exception:
        return None
    return None


def set_privacy_accepted(session_id, accepted=True):
    """Update session with privacy acceptance."""
    oid = ObjectId(session_id)
    sessions_collection.update_one(
        {"_id": oid},
        {"$set": {"privacy_accepted": accepted}}
    )

def save_message(session_id, role, content):
    """Save a message in the DB for a session."""
    message_data = {
        "session_id": session_id,
        "role": role,
        "content": content,
    }
    messages_collection.insert_one(message_data)

def load_messages(session_id):
    """Load all messages for a session."""
    messages_cursor = messages_collection.find({"session_id": session_id}).sort("_id")
    return [{"role": msg["role"], "content": msg["content"]} for msg in messages_cursor]

def clear_session(session_id):
    """Delete all messages for a session."""
    messages_collection.delete_many({"session_id": session_id})

def save_evaluation(session_id, full_name, email, phone, summary, strengths, weaknesses, score):
    """Save a candidate evaluation in the DB for a session."""
    evaluation_data = {
        "session_id": session_id,
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "summary": summary,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "score": score,
    }
    # Use update_one with upsert=True to either insert a new evaluation
    # or update an existing one for the same session_id.
    evaluations_collection.update_one(
        {"session_id": session_id},
        {"$set": evaluation_data},
        upsert=True
    )