# imports libraries

import asyncio
import logging
import json
import aiohttp
import os

# Importing necessary modules and classes

from google.genai import types
from database.firebase_manager import FirebaseManager
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from root_agent import create_root_agent

logging.basicConfig(level=logging.INFO)

# Initialize Firebase manager with your credentials
credentials_path = os.getenv(
    "FIREBASE_CREDENTIALS_PATH",
    "multiagentfintech-firebase-adminsdk-fbsvc-7864e9d383.json",
)
if os.path.exists("/code/app"):  # Deployed environment
    credentials_path = f"/code/app/{credentials_path}"
firebase_manager = FirebaseManager(
    credential_path=credentials_path,
    database_url="https://multiagentfintech-default-rtdb.asia-southeast1.firebasedatabase.app",  # Replace with your Realtime Database URL
)

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

async def process_agent_response(event):
    """Process and display agent response events."""
    print(f"Event ID: {event.id}, Author: {event.author}")

    # Check for specific parts first
    has_specific_part = False
    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "text") and part.text and not part.text.isspace():
                print(f"  Text: '{part.text.strip()}'")

    # Check for final response after specific parts
    final_response = None
    if not has_specific_part and event.is_final_response():
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            # Use colors and formatting to make the final response stand out
            print(
                f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╔══ AGENT RESPONSE ═════════════════════════════════════════{Colors.RESET}"
            )
            print(f"{Colors.CYAN}{Colors.BOLD}{final_response}{Colors.RESET}")
            print(
                f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╚═════════════════════════════════════════════════════════════{Colors.RESET}\n"
            )
        else:
            print(
                f"\n{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}==> Final Agent Response: [No text content in final event]{Colors.RESET}\n"
            )

    return final_response

async def call_agent_async(runner, user_id, session_id, query, financial_data = None):
    """Call the agent asynchronously with the user's query."""
    
    # print(financial_data)
    session = await runner.session_service.get_session(
            app_name="artha", 
            user_id=user_id, 
            session_id=session_id
        )
    if financial_data is None:
        raw_data = session.state.get("user:raw_data", {})
    else:
        raw_data = financial_data
    
    # 👈 Extract state data
    session.state["user:raw_data"] = financial_data

    # print(session.state.get("user:raw_data", {})) # <------- raw_data empty here
    behavioral_summary = session.state.get("behavioral_summary", "")
    current_financial_goals = session.state.get("current_financial_goals", "")
    agent_persona = session.state.get("agent_persona", "")

    # 👈 Create enriched query with financial context
    enriched_query = f"""
    User Query: {query}
    
    Financial Context Available:
    - Raw Financial Data: {json.dumps(raw_data, indent=2) if raw_data else "No data available"}
    - Behavioral Summary: {behavioral_summary}
    - Current Goals: {current_financial_goals}
    - User Persona: {agent_persona}
    
    Please provide personalized financial advice based on this context.
    """
    content = types.Content(role="user", parts=[types.Part(text=enriched_query)])
    print(
        f"\n{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD}--- Running Query: {query} ---{Colors.RESET}"
    )
    final_response_text = None
    agent_name = None
    
    try:
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content): 
            # Capture the agent name from the event if available
            if event.author:
                agent_name = event.author

            response = await process_agent_response(event)
            if response:
                final_response_text = response

        # Save conversation and financial summary to Firebase
        chat_data = {
            'query_user': query,
            'llm_response': final_response_text,
            'timestamps': {'.sv': 'timestamp'}
        }
        firebase_manager.save_chat_history(user_id, session_id, chat_data)
        await firebase_manager.save_financial_state(user_id, session_id)

        return final_response_text if final_response_text else "I apologize, but I couldn't generate insights at the moment."
        
    except Exception as e:
        print(f"{Colors.BG_RED}{Colors.WHITE}ERROR during agent run: {e}{Colors.RESET}")
        print(f"Debug: ADK error details: {e}")
        return f"Error generating insights: {str(e)}"

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
        self.base_url = "https://artha-mcp-server.onrender.com"
        self.session_id = None
        self.authenticated = False

    async def authenticate(self, phone_number, session_id):
        """Complete 3-step authentication following your API documentation"""
        # Use same session ID format that worked in curl
        
        self.session_id = f"mcp-session-{session_id}"

        async with aiohttp.ClientSession() as session:
            # Step 1: Get login URL (this is working in your curl)
            headers = {
                "Content-Type": "application/json",
                "Mcp-Session-Id": self.session_id,
            }

            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "fetch_bank_transactions",  # or any tool name
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
            
            # Step 2: Authorize session using extracted session ID
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
                # Extract the actual data from JSON-RPC response
                content = result.get("result", {}).get("content", [{}])[0]
                return json.loads(content.get("text", "{}"))

mcp_client = FiMCPClient()

async def get_financial_data(phone_number, session_id, data_types=None):
    """Fetch comprehensive financial data from MCP server"""
    if not mcp_client.authenticated:
        await mcp_client.authenticate(phone_number, session_id)

    if data_types is None:
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
            # received JSONs in key value pairs
            
        except Exception as e:
            print(f"Warning: Could not fetch {data_type}: {e}")
            financial_data[data_type] = None

    return financial_data

async def main():
    """Main entry point"""  
    print("🏦 Welcome to Artha - Your AI Financial Advisor")
    print("=" * 50)
    
    root_agent = create_root_agent()
    
    # SETUP SESSION AND RUNNER
    
    session_service = InMemorySessionService()
    phone_number = input("\nEnter your phone number (e.g., 1313131313): ").strip()
    new_session = await session_service.create_session(
        app_name="artha",
        user_id=phone_number,  # Placeholder, will be set per user
        state=initial_state
    )
    session_id = new_session.id
    runner = Runner(
        agent=root_agent,
        app_name="artha",
        session_service=session_service,
    )
    
    # phone number, session id, runner new session
     
    while True:            
            try:
                print("🔐 Authenticating...")
                # Test authentication and data fetching
                financial_data = await get_financial_data(phone_number, session_id)
                session = await session_service.get_session(app_name="artha", user_id=phone_number, session_id=session_id)
                if session is None:
                    session = new_session # check and improve
                session.state["user_id"] = phone_number
                session.state["user:raw_data"] = financial_data
                session.state["behavioral_summary"] = ""
                session.state["current_financial_goals"] = "Maximize savings, invest in mutual funds, and prepare for retirement."
                session.state["agent_persona"] = "conscientious and extroverted"
                
                print("✅ Authentication successful!")
                print("📊 Financial data retrieved successfully!")
                
                # User conversation loop
                while True:
                    user_query = input(f"\n{phone_number} 💬: Ask about your finances (or 'logout'): ").strip()
                    
                    if user_query.lower() == 'logout':
                        mcp_client.authenticated = False
                        break
                    elif user_query.lower() in ['exit', 'quit']:
                        return
                    elif not user_query:
                        continue
                    
                    print("🤖 Artha: Analyzing your request...")
                    
                    # Generate insights using Gemini and specialist agents
                    insights = await call_agent_async(runner, phone_number, session_id, user_query, financial_data) # Call agent aync example 8
                    
                    print("\n" + "="*60)
                    print("📈 ARTHA FINANCIAL INSIGHTS")
                    print("="*60)
                    print(insights)
                    print("="*60)
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Please ensure Fi MCP server is running on port 8080")

if __name__ == "__main__":
    asyncio.run(main())