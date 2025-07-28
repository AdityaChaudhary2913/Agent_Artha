import aiohttp
import json
import uuid
from database.firebase_manager import FirebaseManager

initial_state = {
    "user_id": None,
    "raw_date": [],
    "behavioral_summary": "",
    "current_financial_goals": "",
    "agent_persona": "conscientious and extroverted"
}

class FiMCPClient:
    """Exact copy from your working reference"""
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = "https://artha-mcp-server.onrender.com"
        self.session_id = None
        self.authenticated = False

    async def authenticate(self, phone_number):
        """Complete 3-step authentication following your API documentation"""
        # Use same session ID format that worked in curl
        self.session_id = f"mcp-session-{uuid.uuid4()}"
        
        async with aiohttp.ClientSession() as session:
            # Step 1: Get login URL (this is working in your curl)
            headers = {
                "Content-Type": "application/json",
                "Mcp-Session-Id": self.session_id
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "fetch_bank_transactions", # or any tool name
                    "arguments": {}
                }
            }
            
            async with session.post(
                f"{self.base_url}/mcp/stream",
                headers=headers,
                json=payload
            ) as response:
                result = await response.json()
                content = result.get("result", {}).get("content", [{}])[0]
                login_data = json.loads(content.get("text", "{}"))
                
                if login_data.get("status") != "login_required":
                    raise Exception("Authentication flow error")
            
            # Step 2: Authorize session using extracted session ID
            login_data = {
                "sessionId": self.session_id,
                "phoneNumber": phone_number
            }
            
            async with session.post(
                f"{self.base_url}/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
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
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Mcp-Session-Id": self.session_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/mcp/stream",
                headers=headers,
                json=payload
            ) as response:
                result = await response.json()
                # Extract the actual data from JSON-RPC response
                content = result.get("result", {}).get("content", [{}])[0]
                return json.loads(content.get("text", "{}"))

class FinancialAgent:
    """Following your working reference pattern exactly"""
    def __init__(self, firebase_manager: FirebaseManager):
        self.mcp_client = FiMCPClient()


    async def get_financial_data(self, phone_number, data_types=None):
        """Fetch comprehensive financial data from MCP server"""
        if not self.mcp_client.authenticated:
            await self.mcp_client.authenticate(phone_number)
        
        if data_types is None:
            data_types = [
                "fetch_net_worth",
                "fetch_credit_report",
                "fetch_epf_details",
                "fetch_mutual_funds",
                "fetch_mf_transactions",
                "fetch_bank_transactions",
                "fetch_stock_transactions"
            ]
        
        financial_data = {}
        for data_type in data_types:
            try:
                data = await self.mcp_client.call_tool(data_type)
                financial_data[data_type] = data
            except Exception as e:
                print(f"Warning: Could not fetch {data_type}: {e}")
                financial_data[data_type] = None

        return financial_data

# Create a global instance to be used by main.py
def create_financial_advisor(firebase_manager: FirebaseManager):
    """Factory function to create the financial advisor"""
    return FinancialAgent(firebase_manager)
