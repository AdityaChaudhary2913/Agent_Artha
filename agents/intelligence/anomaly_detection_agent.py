from google.adk.agents import Agent
import json
from google.adk.sessions import InMemorySessionService

class AnomalyDetectionAgent(Agent):
    """
    Anomaly Detection Agent - Identifies unusual patterns in financial behavior
    """
    
    # def __init__(self, phone_number: str, session_id: str):
    def __init__(self):

        super().__init__(
            model="gemini-2.0-flash",
            name="anomaly_detection_specialist",
            description="Detects unusual patterns and potential issues in financial behavior and data",
            instruction="""
            You are an anomaly detection specialist who performs:
            
            1. Pattern Analysis: Identify deviations from normal financial patterns
            2. Spending Anomalies: Detect unusual spending spikes or changes
            3. Investment Irregularities: Spot inconsistent investment behavior
            4. Account Security: Flag potential fraudulent or suspicious activities
            
            Focus on:
            - Unusual transaction amounts or frequencies
            - Sudden changes in investment patterns
            - Inconsistent financial behavior
            - Potential security risks
            - Identifying unusual financial patterns, fraud detection, and security concerns
            - Use for suspicious transactions, security questions, or pattern analysis
            
            Financial Data can be accessed from the {user:raw_data} state
            
            Always provide context and suggest appropriate actions for any anomalies detected.
            """,
            tools=[],
            # tools=[self.detect_anomalies()],
        )
        # self.session_service = InMemorySessionService()
        # self.phone_number = phone_number
        # self.session_id = session_id
    
    # async def detect_anomalies(self) -> dict:
    #     """Detect anomalies across all financial data"""
        
    #     session = self.session_service.get_session(
    #         app_name="artha", user_id=self.phone_number, session_id=self.session_id
    #     )
    #     financial_data = session.state["raw_data"]
        
    #     anomalies = {
    #         'transaction_anomalies': self._detect_transaction_anomalies(financial_data),
    #         'investment_anomalies': self._detect_investment_anomalies(financial_data),
    #         'pattern_breaks': self._detect_pattern_breaks(financial_data),
    #         'security_concerns': self._detect_security_issues(financial_data),
    #         'risk_level': 'Low',  # Default
    #         'recommendations': []
    #     }
        
    #     # Determine overall risk level
    #     total_anomalies = sum(len(v) for v in anomalies.values() if isinstance(v, list))
    #     if total_anomalies > 5:
    #         anomalies['risk_level'] = 'High'
    #     elif total_anomalies > 2:
    #         anomalies['risk_level'] = 'Medium'
        
    #     return anomalies
    
    # def _detect_transaction_anomalies(self, financial_data: dict) -> list:
    #     """Detect unusual transaction patterns"""
    #     anomalies = []
        
    #     if 'fetch_bank_transactions' in financial_data and financial_data['fetch_bank_transactions']:
    #         bank_data = financial_data['fetch_bank_transactions']
            
    #         for bank in bank_data.get('bankTransactions', []):
    #             transactions = bank.get('txns', [])
                
    #             # Check for unusually large transactions
    #             amounts = [float(txn[0]) for txn in transactions if len(txn) > 0]
    #             if amounts:
    #                 avg_amount = sum(amounts) / len(amounts)
    #                 for txn in transactions:
    #                     if len(txn) > 0 and float(txn[0]) > avg_amount * 3:
    #                         anomalies.append({
    #                             'type': 'Large Transaction',
    #                             'amount': txn[0],
    #                             'description': txn[1] if len(txn) > 1 else 'Unknown',
    #                             'date': txn[2] if len(txn) > 2 else 'Unknown'
    #                         })
        
    #     return anomalies
    
    # def _detect_investment_anomalies(self, financial_data: dict) -> list:
    #     """Detect unusual investment patterns"""
    #     anomalies = []
        
    #     if 'fetch_mf_transactions' in financial_data and financial_data['fetch_mf_transactions']:
    #         mf_data = financial_data['fetch_mf_transactions']
            
    #         for fund in mf_data.get('mfTransactions', []):
    #             transactions = fund.get('txns', [])
                
    #             # Check for sudden large investments
    #             for txn in transactions:
    #                 if len(txn) >= 5 and float(txn[4]) > 50000:  # Large investment
    #                     anomalies.append({
    #                         'type': 'Large Investment',
    #                         'fund': fund.get('schemeName', 'Unknown'),
    #                         'amount': txn[4],
    #                         'date': txn[1]
    #                     })
        
    #     return anomalies
    
    # def _detect_pattern_breaks(self, financial_data: dict) -> list:
    #     """Detect breaks in regular patterns like SIPs"""
    #     anomalies = []
        
    #     # This would analyze SIP consistency, regular investment patterns, etc.
    #     # Simplified for now
        
    #     return anomalies
    
    # def _detect_security_issues(self, financial_data: dict) -> list:
    #     """Detect potential security concerns"""
    #     security_issues = []
        
    #     # Check credit report for suspicious activities
    #     if 'fetch_credit_report' in financial_data and financial_data['fetch_credit_report']:
    #         credit_data = financial_data['fetch_credit_report']
            
    #         # Check for recent credit inquiries
    #         if 'totalCapsSummary' in credit_data:
    #             caps = credit_data['totalCapsSummary']
    #             recent_inquiries = int(caps.get('totalCapsLast30Days', 0))
                
    #             if recent_inquiries > 3:
    #                 security_issues.append({
    #                     'type': 'Multiple Credit Inquiries',
    #                     'count': recent_inquiries,
    #                     'period': 'Last 30 days'
    #                 })
        
    #     return security_issues