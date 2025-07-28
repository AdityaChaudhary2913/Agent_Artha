from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from agents.strategic.market_intelligence_agent import MarketIntelligenceAgent


class CulturalEventsAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model="gemini-2.0-flash",
            name="cultural_events_specialist",
            description=
            """
            Plans for cultural and family financial obligations
            """,
            instruction=
            """
            You help plan finances for Indian cultural events, festivals, weddings, and family obligations. 
            Use the Market Intelligence Agent for real-time data on local events and trends of Bangalore. Also, use the internet to get today's date, and if
            there are any Indian festivals coming up, let the user know and help them arrange their finances accordingly by giving them a rough
            spending budget range.
            Focus on budgeting, saving, and investment strategies that align with cultural practices.
            """,
            tools=[AgentTool(MarketIntelligenceAgent())],  # Used as a web search tool for real-time data

        )