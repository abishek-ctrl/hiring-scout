import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()

# --- MongoDB Connection ---
def get_mongo_client():
    connection_string = os.environ.get("MONGO_CONNECTION_STRING")
    client = MongoClient(connection_string)
    return client

def init_db():
    client = get_mongo_client()
    db = client.hiring_scout_db
    return db.sessions, db.messages, db.evaluations

sessions_collection, messages_collection, evaluations_collection = init_db()

def get_or_create_user_session(name: str, email: str, phone: str):
    query = {"$or": [{"email": email}, {"phone": phone}]}
    latest_evaluation = evaluations_collection.find_one(query, sort=[("_id", -1)])

    if latest_evaluation:
        return latest_evaluation["session_id"], False
    else:
        session_data = {"privacy_accepted": True}
        result = sessions_collection.insert_one(session_data)
        new_session_id = str(result.inserted_id)
        
        initial_evaluation = {
            "session_id": new_session_id,
            "full_name": name,
            "email": email,
            "phone": phone,
        }
        evaluations_collection.insert_one(initial_evaluation)
        
        return new_session_id, True

def delete_all_user_data(email: str, phone: str):
    """
    Finds and deletes ALL data for a user based on their email or phone.
    This is a true "right to be forgotten" function.
    """
    query = {"$or": [{"email": email}, {"phone": phone}]}
    user_evaluations = list(evaluations_collection.find(query))

    if not user_evaluations:
        return

    session_ids_to_delete = list(set(eval_doc["session_id"] for eval_doc in user_evaluations))
    session_object_ids_to_delete = [ObjectId(sid) for sid in session_ids_to_delete]

    if session_ids_to_delete:
        messages_collection.delete_many({"session_id": {"$in": session_ids_to_delete}})
        evaluations_collection.delete_many({"session_id": {"$in": session_ids_to_delete}})
        sessions_collection.delete_many({"_id": {"$in": session_object_ids_to_delete}})

def load_messages(session_id):
    messages_cursor = messages_collection.find({"session_id": session_id}).sort("_id")
    return [{"role": msg["role"], "content": msg["content"]} for msg in messages_cursor]

def save_message(session_id, role, content):
    message_data = {"session_id": session_id, "role": role, "content": content}
    messages_collection.insert_one(message_data)

def save_evaluation(session_id, full_name, email, phone, years_of_experience, current_location, tech_stack, summary, strengths, weaknesses, score):
    evaluation_data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "years_of_experience": years_of_experience,
        "current_location": current_location,
        "tech_stack": tech_stack,
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