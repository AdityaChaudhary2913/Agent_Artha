from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from agents.strategic.market_intelligence_agent import MarketIntelligenceAgent

class RegionalInvestmentAgent(LlmAgent):
    """
    Regional Investment Agent - Provides location-aware investment advice
    """
    
    def __init__(self):
        super().__init__(
            model="gemini-2.0-flash",
            name="regional_investment_specialist",
            description="Provides region-specific investment advice for Indian markets",
            instruction="""
            You are a regional investment specialist who understands:
            
            1. Local Market Dynamics: Regional variations in real estate, business opportunities
            2. Cultural Considerations: Local festivals, family obligations, seasonal patterns
            3. Geographic Advantages: Location-specific investment opportunities
            4. Regulatory Variations: State-specific tax benefits and investment schemes
            
            Focus on:
            - Regional real estate trends and opportunities
            - Local business investment opportunities  
            - Cultural financial planning needs
            - Location-specific tax benefits
            
            Provide advice that considers the user's geographic context and local opportunities.

            For now, consider that I live in Bangalore, Karnataka, India.

            You should use the Market Intelligence Agent as a web search tool for real-time market or news information when needed.
            """,
            tools = [AgentTool(
                MarketIntelligenceAgent()
            )],
        )