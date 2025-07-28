from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from agents.strategic.market_intelligence_agent import MarketIntelligenceAgent


class IlliquidAssetAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model="gemini-2.0-flash",
            name="illiquid_asset_specialist",
            description="""Manages gold, real estate, and other illiquid investments""", 
            instruction=
            """
            You provide advice on illiquid assets like gold, real estate, and alternative investments. 
            You can use the market intelligence agent available as a tool for real-time data. Focus on long-term value, mrket trends, and cultural factors in investment decisions.
            """,
            tools=[
            AgentTool(
                MarketIntelligenceAgent()
            ),  # Used as a web search tool; add MCP as tool later?
        ],
        )