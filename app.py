from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os
import aiohttp
import json
from google.genai import types
from database.firebase_manager import FirebaseManager
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from root_agent import create_root_agent

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI()

# Initialize FirebaseManager
firebase_manager = FirebaseManager()

class Message(BaseModel):
    user_id: str
    session_id: str
    query: str

initial_state = {
    "user_id": "",
    "user:raw_data": {},
    "behavioral_summary": "",
    "current_financial_goals": "",
    "agent_persona": "conscientious and extroverted",
}

class FiMCPClient:
    """Exact copy from your working reference"""

    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = os.getenv("FIMCP_BASE_URL", base_url)
        self.session_id = None
        self.authenticated = False

    async def authenticate(self, phone_number, session_id):
        """Complete 3-step authentication following your API documentation"""
        self.session_id = f"mcp-session-{session_id}"
        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Mcp-Session-Id": self.session_id,
            }
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "fetch_bank_transactions",
                    "arguments": {},
                },
            }
            async with session.post(
                f"{self.base_url}/mcp/stream", headers=headers, json=payload
            ) as response:
                result = await response.json()
                content = result.get("result", {}).get("content", [{}])[0]
                login_data = json.loads(content.get("text", "{}"))

                if login_data.get("status") != "login_required":
                    raise Exception("Authentication flow error")
            login_data = {"sessionId": self.session_id, "phoneNumber": phone_number}
            async with session.post(
                f"{self.base_url}/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            ) as response:
                if response.status == 200:
                    self.authenticated = True
                    return True
                else:
                    raise Exception(f"Login failed: {response.status}")

    async def call_tool(self, tool_name, arguments=None):
        """Make authenticated tool call using JSON-RPC 2.0"""
        if not self.authenticated:
            raise Exception("Not authenticated. Call authenticate() first.")
        if arguments is None:
            arguments = {}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }
        headers = {
            "Content-Type": "application/json",
            "Mcp-Session-Id": self.session_id,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/mcp/stream", headers=headers, json=payload
            ) as response:
                result = await response.json()
                content = result.get("result", {}).get("content", [{}])[0]
                return json.loads(content.get("text", "{}"))

mcp_client = FiMCPClient()

async def process_agent_response(event):
    """Process and display agent response events."""
    final_response = None
    if event.is_final_response():
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
    return final_response

async def get_financial_data(phone_number, session_id):
    """Fetch comprehensive financial data from MCP server"""
    if not mcp_client.authenticated:
        await mcp_client.authenticate(phone_number, session_id)

    data_types = [
        "fetch_net_worth",
        "fetch_credit_report",
        "fetch_epf_details",
        "fetch_mutual_funds",
        "fetch_mf_transactions",
        "fetch_bank_transactions",
        "fetch_stock_transactions",
    ]

    financial_data = {}
    for data_type in data_types:
        try:
            data = await mcp_client.call_tool(data_type)
            financial_data[data_type] = data
        except Exception as e:
            print(f"Warning: Could not fetch {data_type}: {e}")
            financial_data[data_type] = None

    return financial_data

financial_data = None

"""
{
    "user_id": "1313131313",
    "session_id": "7b714dfd-cc65-4d36-b6ba-631b62376f3a",
    "query": "This is a session which is added for testing purpose, so please give some basic financial insights based on my financial data.",
}
"""
@app.post("/start/")
async def add_message(message: Message):
    try:
        key = None
        # HARDCODE this to start a new session (for frontend)
        if message.query != "" and message.session_id != "":
            chat_data = {
                "query_user": message.query,
                "llm_thinking": "",
                "llm_response": "",
                "timestamps": {".sv": "timestamp"},
            }
            key = firebase_manager.save_chat_history(
                user_id=message.user_id,
                session_id=message.session_id,
                chat_data=chat_data
            )
        session_service = InMemorySessionService()
        runner = Runner(
            agent=create_root_agent(),
            app_name="artha",
            session_service=session_service,
        )
        session = None
        try:
            session = await runner.session_service.get_session(
                app_name="artha", user_id=message.user_id, session_id=message.session_id
            )
            if session is None:
                print("Debug: Session not found, creating a new one.")
                raise HTTPException(status_code=500, detail="Session could not be Retrieved!")
        except HTTPException :
            session = await session_service.create_session(
                app_name="artha",
                user_id=message.user_id,
                state=initial_state,
            )
            if session is None:
                raise HTTPException(status_code=500, detail="Session could not be Created!")
            financial_data = await get_financial_data(message.user_id, session.id)
            if message.query == "" and message.session_id == "":
                firebase_manager.save_new_session(message.user_id, session.id)
                return {"status": "success", "message": "New session created.", "session_id": session.id}
        raw_data = None
        try:
            if financial_data is None:
                raw_data = session.state.get("user:raw_data", {})
        except KeyError:
            raw_data = financial_data
        
        # 👈 Extract state data
        print("State: ", session.state.get("user:raw_data", {})) # <------- raw_data empty here
        session.state["user:raw_data"] = financial_data
        behavioral_summary = session.state.get("behavioral_summary", "")
        current_financial_goals = session.state.get("current_financial_goals", "")
        agent_persona = session.state.get("agent_persona", "")

        # 👈 Create enriched query with financial context
        enriched_query = f"""
        User Query: {message.query}
        
        Financial Context Available:
        - Raw Financial Data: {json.dumps(raw_data, indent=2) if raw_data else "No data available"}
        - Behavioral Summary: {behavioral_summary}
        - Current Goals: {current_financial_goals}
        - User Persona: {agent_persona}
        
        Please provide personalized financial advice based on this context.
        """
        content = types.Content(role="user", parts=[types.Part(text=enriched_query)])
        final_response_text = None
        accumulated_thinking = []  # Track thinking steps across all events
        
        try:
            async for event in runner.run_async(user_id=message.user_id, session_id=session.id, new_message=content): 
                # Collect thinking parts from this event
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text and not part.text.isspace():
                            thinking_text = part.text.strip()
                            print(f"  Text: '{thinking_text}'")
                            accumulated_thinking.append(thinking_text)
                            
                            # Send accumulated thinking to Firebase in real-time
                            if firebase_manager and key:
                                combined_thinking = "\n".join(accumulated_thinking)
                                firebase_manager.update_llm_thinking(message.user_id, message.session_id, key, combined_thinking)
                
                response = await process_agent_response(event)
                if response:
                    final_response_text = response

            # Save conversation and financial summary to Firebase
            chat_data = {
                'query_user': message.query,
                'llm_response': final_response_text,
                'timestamps': {'.sv': 'timestamp'}
            }
            print("Response: ", message.query, final_response_text)
            firebase_manager.save_chat_history2(message.user_id, message.session_id, chat_data, key=key)
            await firebase_manager.save_financial_state(message.user_id, message.session_id)
            return (
                {"status": "success", "message": "Message added successfully."}
                if final_response_text
                else {"status": "error", "message": "I apologize, but I couldn't generate insights at the moment."}
            )
        except Exception as e:
            print(f"Debug: ADK error details: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
