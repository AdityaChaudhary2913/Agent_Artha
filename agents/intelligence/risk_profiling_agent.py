from google.adk.agents import LlmAgent
import json
from google.adk.sessions import InMemorySessionService

class RiskProfilingAgent(LlmAgent):
    """
    Risk Profiling Agent - Analyzes user's risk tolerance and behavioral patterns
    """
    
    # def __init__(self, phone_number: str, session_id: str):
    def __init__(self):
        super().__init__(
            model="gemini-2.0-flash",
            name="risk_profiling_specialist",
            description="Analyzes user risk tolerance, investment behavior, and provides behavioral finance insights",
            instruction="""
            You are a risk profiling specialist who:
            
            1. Behavioral Analysis: Study transaction patterns to understand risk appetite
            2. Portfolio Assessment: Evaluate asset allocation for risk appropriateness  
            3. Emotional Finance: Detect potential emotional investment decisions
            4. Risk Recommendations: Suggest portfolio adjustments based on risk profile
            
            Key areas to analyze:
            - Asset allocation across equity, debt, and other instruments
            - Investment frequency and amounts (SIP vs lump sum)
            - Market timing behavior (buying during peaks/troughs)
            - Diversification levels across sectors and asset classes
            - Emergency fund adequacy
            
            Financial Data can be accessed from the {user:raw_data} state
            
            Provide specific recommendations for Indian investors considering their life stage, income, and goals.
            """,
            tools=[],
        )
        # self.session_service = InMemorySessionService()
        # self.phone_number = phone_number
        # self.session_id = session_id
    
    # async def analyze_risk_profile(self) -> dict:
    #     """Analyze user's risk profile based on investment behavior"""
        
    #     session = self.session_service.get_session(
    #         app_name="artha", user_id=self.phone_number, session_id=self.session_id
    #     )
    #     financial_data = session.state["raw_data"]
        
    #     risk_indicators = self._extract_risk_indicators(financial_data)
    #     risk_score = self._calculate_risk_score(risk_indicators)
    #     behavioral_insights = self._analyze_behavioral_patterns(financial_data)
        
    #     return {
    #         'risk_tolerance': self._categorize_risk_tolerance(risk_score),
    #         'risk_score': risk_score,
    #         'risk_indicators': risk_indicators,
    #         'behavioral_insights': behavioral_insights,
    #         'recommendations': self._generate_risk_recommendations(risk_score, financial_data)
    #     }
    
    # def _extract_risk_indicators(self, financial_data: dict) -> dict:
    #     """Extract key risk indicators from financial data"""
    #     indicators = {}
        
    #     # Analyze asset allocation if net worth data is available
    #     if 'fetch_net_worth' in financial_data and financial_data['fetch_net_worth']:
    #         net_worth_data = financial_data['fetch_net_worth']
    #         assets = net_worth_data.get('netWorthResponse', {}).get('assetValues', [])
            
    #         total_assets = 0
    #         equity_allocation = 0
            
    #         for asset in assets:
    #             asset_type = asset.get('netWorthAttribute', '')
    #             value = float(asset.get('value', {}).get('units', 0))
    #             total_assets += value
                
    #             if 'MUTUAL_FUND' in asset_type or 'SECURITIES' in asset_type:
    #                 equity_allocation += value
            
    #         indicators['equity_percentage'] = (equity_allocation / total_assets * 100) if total_assets > 0 else 0
        
    #     # Analyze SIP behavior
    #     if 'fetch_mf_transactions' in financial_data and financial_data['fetch_mf_transactions']:
    #         indicators['sip_consistency'] = self._analyze_sip_patterns(financial_data['fetch_mf_transactions'])
        
    #     return indicators
    
    # def _calculate_risk_score(self, indicators: dict) -> float:
    #     """Calculate numerical risk score (0-100)"""
    #     score = 50  # Base score
        
    #     # Adjust based on equity allocation
    #     equity_pct = indicators.get('equity_percentage', 0)
    #     if equity_pct > 80:
    #         score += 20
    #     elif equity_pct > 60:
    #         score += 10
    #     elif equity_pct < 30:
    #         score -= 15
        
    #     return max(0, min(100, score))
    
    # def _categorize_risk_tolerance(self, risk_score: float) -> str:
    #     """Categorize risk tolerance based on score"""
    #     if risk_score >= 70:
    #         return "High Risk Tolerance"
    #     elif risk_score >= 40:
    #         return "Moderate Risk Tolerance" 
    #     else:
    #         return "Conservative Risk Tolerance"
    
    # def _analyze_behavioral_patterns(self, financial_data: dict) -> list:
    #     """Analyze behavioral finance patterns"""
    #     patterns = []
        
    #     # Add behavioral analysis logic here
    #     patterns.append("Regular SIP investor - shows disciplined investment behavior")
        
    #     return patterns
    
    # def _analyze_sip_patterns(self, mf_data: dict) -> str:
    #     """Analyze SIP consistency patterns"""
    #     # Simplified analysis
    #     return "Consistent"
    
    # def _generate_risk_recommendations(self, risk_score: float, financial_data: dict) -> list:
    #     """Generate risk-based recommendations"""
    #     recommendations = []
        
    #     if risk_score > 70:
    #         recommendations.append("Consider balancing your high-risk portfolio with some debt instruments")
    #     elif risk_score < 40:
    #         recommendations.append("You may benefit from gradually increasing equity allocation for better long-term returns")
            
    #     return recommendations