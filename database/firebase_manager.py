import firebase_admin
from firebase_admin import credentials, db
import logging
import os
import json
from google.adk.sessions import InMemorySessionService
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FirebaseManager:
    """
    Firebase Manager with flexible credential loading.
    
    Priority order for Firebase credentials:
    1. Environment variables (FIREBASE_PRIVATE_KEY, FIREBASE_CLIENT_EMAIL, etc.)
    2. FIREBASE_CREDENTIALS environment variable (JSON string)
    3. JSON file path (fallback for local development)
    """
    def __init__(self, credential_path=None, database_url=None):
        try:
            # First priority: Use service account credentials from environment variables
            firebase_config = self._get_firebase_config_from_env()
            
            if firebase_config:
                # Use environment variables to create Firebase configuration
                cred = credentials.Certificate(firebase_config)
                db_url = os.getenv('FIREBASE_DATABASE_URL')
                logging.info("Using Firebase credentials from environment variables")
            else:
                # Fallback: Try to use FIREBASE_CREDENTIALS environment variable (for Railway deployment)
                firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
                if firebase_credentials:
                    # Parse JSON from environment variable
                    cred_dict = json.loads(firebase_credentials)
                    cred = credentials.Certificate(cred_dict)
                    db_url = database_url or os.getenv('FIREBASE_DATABASE_URL')
                    logging.info("Using Firebase credentials from FIREBASE_CREDENTIALS environment variable")
                else:
                    # Last fallback: Use file path for local development
                    if not credential_path:
                        credential_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'multiagentfintech-firebase-adminsdk-fbsvc-7864e9d383.json')
                    
                    if not os.path.exists(credential_path):
                        raise ValueError(f"Firebase credentials file not found: {credential_path}")
                    
                    cred = credentials.Certificate(credential_path)
                    db_url = database_url or os.getenv('FIREBASE_DATABASE_URL')
                    logging.info(f"Using Firebase credentials from file: {credential_path}")
                
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred, {
                    'databaseURL': db_url
                })
            self.db = db.reference()
            logging.info("Firebase Realtime Database initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {e}")
            self.db = None
        
        self.session_service = InMemorySessionService()

    def _get_firebase_config_from_env(self):
        """Create Firebase service account configuration from environment variables"""
        try:
            # Get service account credentials from environment variables
            firebase_project_id = os.getenv('FIREBASE_PROJECT_ID')
            firebase_private_key_id = os.getenv('FIREBASE_PRIVATE_KEY_ID')
            firebase_private_key = os.getenv('FIREBASE_PRIVATE_KEY')
            firebase_client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
            firebase_client_id = os.getenv('FIREBASE_CLIENT_ID')
            firebase_client_cert_url = os.getenv('FIREBASE_CLIENT_CERT_URL')
            
            # Check if minimum required variables are present for service account
            if not all([firebase_project_id, firebase_private_key, firebase_client_email]):
                return None
            
            # Construct service account configuration
            config = {
                "type": "service_account",
                "project_id": firebase_project_id,
                "private_key_id": firebase_private_key_id or "",
                "private_key": firebase_private_key.replace('\\n', '\n') if firebase_private_key else "",
                "client_email": firebase_client_email,
                "client_id": firebase_client_id or "",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": firebase_client_cert_url or f"https://www.googleapis.com/robot/v1/metadata/x509/{firebase_client_email.replace('@', '%40') if firebase_client_email else 'unknown'}"
            }
            
            return config
            
        except Exception as e:
            logging.error(f"Error creating Firebase config from environment: {e}")
            return None

    def save_new_session(self, user_id, session_id):
        if not self.db:
            logging.error("Realtime Database client not available.")
            return None
        try:
            chat_history_ref = (self.db.child("users").child(user_id).child("chats").child(session_id))
            chat_history_ref.push()
        except Exception as e:
            logging.error(f"Failed to save new chat session: {e}")
            return None
    
    def save_chat_history(self, user_id, session_id, chat_data):
        if not self.db:
            logging.error("Realtime Database client not available.")
            return None
        try:
            chat_history_ref = (
                self.db.child("users").child(user_id).child("chats").child(session_id)
            )
            newRef = chat_history_ref.push()
            key = newRef.key
            newRef.child("query_user").set(chat_data["query_user"])
            newRef.child("llm_response").set(chat_data["llm_response"])
            newRef.child("timestamps").set(chat_data["timestamps"])
            logging.info(
                f"Chat history saved for user {user_id} in session {session_id}."
            )
            return key
        except Exception as e:
            logging.error(f"Failed to save chat history: {e}")
            return None

    def save_chat_history2(self, user_id, session_id, chat_data, key):
        if not self.db:
            logging.error("Realtime Database client not available.")
            return
        
        if key is None:
            logging.error("Invalid key provided: key cannot be None")
            return
            
        try:
            chat_history_ref = (
                self.db.child("users").child(user_id).child("chats").child(session_id)
            )
            newRef = chat_history_ref.child(key)
            newRef.child("query_user").set(chat_data["query_user"])
            newRef.child("llm_response").set(chat_data["llm_response"])
            newRef.child("timestamps").set(chat_data["timestamps"])
            logging.info(
                f"Chat history saved for user {user_id} in session {session_id}."
            )
        except Exception as e:
            logging.error(f"Failed to save chat history2: {e}")
    
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

    def update_llm_thinking(self, user_id, session_id, key, thinking_text):
        """Update LLM thinking steps in real-time to Firebase"""
        if not self.db:
            logging.error("Realtime Database client not available.")
            return
        
        if key is None:
            logging.error("Invalid key provided: key cannot be None")
            return
            
        try:
            chat_ref = (
                self.db.child("users").child(user_id).child("chats").child(session_id).child(key)
            )
            chat_ref.child("llm_thinking").set(thinking_text)
            logging.info(f"LLM thinking updated for user {user_id} in session {session_id}")
        except Exception as e:
            logging.error(f"Failed to update LLM thinking: {e}")

