from google.adk.agents import LlmAgent

class DebtManagementAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            model="gemini-2.0-flash",
            name="debt_management_specialist",
            description=
            """
            An expert agent that analyzes user debt data, 
            current financial goals, and behavioral patterns to optimize 
            debt repayment strategies, recommend loan consolidation, and 
            improve credit management.
            """,
            instruction=
            """
            You are a debt management specialist. 
            Given the user's raw financial data ({user:raw_data}), 
            their current financial goals ({current_financial_goals}), 
            and a summary of their financial behaviors ({behavioral_summary}), 
            analyze their situation and provide actionable, step-by-step 
            recommendations for optimizing debt repayment, consolidating loans if beneficial, 
            "and improving credit management. Be specific and concise.
            """,
            tools=[],
        )