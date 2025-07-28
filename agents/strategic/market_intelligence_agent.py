from google.adk.agents import Agent
from google.adk.agents import Agent
from google.adk.tools import google_search

class MarketIntelligenceAgent(Agent):
    def __init__(self):
        super().__init__(
            model="gemini-2.0-flash",
            name="market_intelligence_specialist",
            description="""Provides market analysis and investment timing insights""",
            instruction="""You analyze market conditions, trends, and provide investment timing advice for Indian markets.""",
            tools=[google_search],
        
        )