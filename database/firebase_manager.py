import firebase_admin
from firebase_admin import credentials, db
import logging
from google.adk.sessions import InMemorySessionService

class FirebaseManager:
    def __init__(self, credential_path, database_url):
        try:
            cred = credentials.Certificate(credential_path)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred, {
                    'databaseURL': database_url
                })
            self.db = db.reference()
            logging.info("Firebase Realtime Database initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {e}")
            self.db = None
        
        self.session_service = InMemorySessionService()

    def save_chat_history(self, user_id, session_id, chat_data):
        if not self.db:
            logging.error("Realtime Database client not available.")
            return
        
        try:
            chat_history_ref = self.db.child('users').child(user_id).child('chats').child(session_id)
            chat_history_ref.push(chat_data)
            logging.info(f"Chat history saved for user {user_id} in session {session_id}.")
        except Exception as e:
            logging.error(f"Failed to save chat history: {e}")

    async def save_financial_state(self, user_id, session_id):  # 👈 Make this async
        if not self.db:
            logging.error("Realtime Database client not available.")
            return
        
        try:
            # 👈 Await the get_session call
            session = await self.session_service.get_session(
                app_name="artha", 
                user_id=user_id, 
                session_id=session_id
            )
            
            if session is None:
                logging.error(f"Session not found for user {user_id}")
                return
            
            raw_data = session.state.get("raw_data", {})
            financial_state_ref = self.db.child("users").child(user_id).child("raw_data")
            financial_state_ref.set(raw_data)
            
            behavioral_summary = session.state.get("behavioral_summary", "")
            behavioral_state_ref = self.db.child("users").child(user_id).child("behavioral_summary")
            behavioral_state_ref.set(behavioral_summary)
            
            current_financial_goals = session.state.get("current_financial_goals", "")
            goals_state_ref = self.db.child("users").child(user_id).child("current_financial_goals")
            goals_state_ref.set(current_financial_goals)
            
            agent_persona = session.state.get("agent_persona", "")
            persona_state_ref = self.db.child("users").child(user_id).child("agent_persona")
            persona_state_ref.set(agent_persona)
            
            logging.info(f"Financial summary saved for user {user_id}.")
        except Exception as e:
            logging.error(f"Failed to save financial summary for user {user_id}: {e}")


# import firebase_admin
# from firebase_admin import credentials, db
# import logging
# from google.adk.sessions import InMemorySessionService

# class FirebaseManager:
#     def __init__(self, credential_path, database_url):
#         try:
#             cred = credentials.Certificate(credential_path)
#             if not firebase_admin._apps:
#                 firebase_admin.initialize_app(cred, {
#                     'databaseURL': database_url
#                 })
#             self.db = db.reference()
#             logging.info("Firebase Realtime Database initialized successfully.")
#         except Exception as e:
#             logging.error(f"Failed to initialize Firebase: {e}")
#             self.db = None
#         self.session_service = InMemorySessionService()
        

#     def save_chat_history(self, user_id, session_id, chat_data):
#         if not self.db:
#             logging.error("Realtime Database client not available.")
#             return

#         try:
#             chat_history_ref = self.db.child('users').child(user_id).child('chats').child(session_id)
#             chat_history_ref.push(chat_data)
#             logging.info(f"Chat history saved for user {user_id} in session {session_id}.")
#         except Exception as e:
#             logging.error(f"Failed to save chat history: {e}")

#     def save_financial_state(self, user_id, session_id):
#         if not self.db:
#             logging.error("Realtime Database client not available.")
#             return
#         try:
#             session = self.session_service.get_session(app_name="artha", user_id=user_id, session_id=session_id)
            
            
#             raw_data = session.state["raw_data"]
            
#             financial_state_ref = self.db.child("users").child(user_id).child(raw_data)
#             financial_state_ref.set(raw_data)
            
#             behavioral_summary = session.state["behavioral_summary"]
#             behavioral_state_ref = (
#                 self.db.child("users").child(user_id).child(behavioral_summary)
#             )
#             behavioral_state_ref.set(behavioral_summary)
            
#             current_financial_goals = session.state["current_financial_goals"]
#             goals_state_ref = self.db.child("users").child(user_id).child(current_financial_goals)
#             goals_state_ref.set(current_financial_goals)
            
#             agent_persona = session.state["agent_persona"]
#             persona_state_ref = self.db.child("users").child(user_id).child(agent_persona)
#             persona_state_ref.set(agent_persona)
            
            
#             logging.info(f"Financial summary saved for user {user_id}.")
#         except Exception as e:
#             logging.error(f"Failed to save financial summary for user {user_id}: {e}")
            
# initial_state = {
#     "user_id": None,
#     "raw_date": [],
#     "behavioral_summary": "",
#     "current_financial_goals": "",
#     "agent_persona": "conscientious and extroverted",
# }