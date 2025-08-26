import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId

# --- MongoDB Connection ---
def get_mongo_client():
    connection_string = st.secrets["MONGO_CONNECTION_STRING"]
    client = MongoClient(connection_string)
    return client

def init_db():
    client = get_mongo_client()
    db = client.hiring_scout_db
    return db.sessions, db.messages, db.evaluations

sessions_collection, messages_collection, evaluations_collection = init_db()

def get_or_create_user_session(name: str, email: str, phone: str):
    """
    Finds a returning user's session or creates a new one.
    Returns the session_id and a boolean indicating if the user is new.
    """
    # Build a query to find a match for either email or phone
    query = {"$or": [{"email": email}, {"phone": phone}]}
    latest_evaluation = evaluations_collection.find_one(query, sort=[("_id", -1)])

    if latest_evaluation:
        # --- RETURNING USER ---
        session_id = latest_evaluation["session_id"]
        return session_id, False # False means is_new_user = False
    else:
        # --- NEW USER ---
        # 1. Create a new session document
        session_data = {"privacy_accepted": True}
        result = sessions_collection.insert_one(session_data)
        new_session_id = str(result.inserted_id)

        # 2. Immediately create a basic evaluation record to "claim" this user
        initial_evaluation = {
            "session_id": new_session_id,
            "full_name": name,
            "email": email,
            "phone": phone,
        }
        evaluations_collection.insert_one(initial_evaluation)
        
        return new_session_id, True # True means is_new_user = True

def get_session(session_id):
    try:
        oid = ObjectId(session_id)
        session = sessions_collection.find_one({"_id": oid})
        if session:
            session['id'] = str(session['_id'])
            return session
    except Exception:
        return None
    return None

def set_privacy_accepted(session_id, accepted=True):
    oid = ObjectId(session_id)
    sessions_collection.update_one({"_id": oid}, {"$set": {"privacy_accepted": accepted}})

def save_message(session_id, role, content):
    message_data = {"session_id": session_id, "role": role, "content": content}
    messages_collection.insert_one(message_data)

def load_messages(session_id):
    messages_cursor = messages_collection.find({"session_id": session_id}).sort("_id")
    return [{"role": msg["role"], "content": msg["content"]} for msg in messages_cursor]

def clear_session(session_id):
    oid = ObjectId(session_id)
    messages_collection.delete_many({"session_id": session_id})
    evaluations_collection.delete_many({"session_id": session_id})
    sessions_collection.delete_one({"_id": oid})

def save_evaluation(session_id, full_name, email, phone, summary, strengths, weaknesses, score):
    evaluation_data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "summary": summary,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "score": score,
    }
    evaluations_collection.update_one(
        {"session_id": session_id},
        {"$set": evaluation_data},
        upsert=True
    )