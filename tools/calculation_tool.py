class CalculationTool:
    """Tool for financial calculations - Simple Python Class"""
    
    def __init__(self):
        self.name = "financial_calculator"
        self.description = "Perform financial calculations like SIP returns, loan EMI, compound interest, etc."
    
    def calculate(self, calculation_type: str, **kwargs) -> str:
        """Perform various financial calculations"""
        try:
            if calculation_type == "sip_future_value":
                return self._calculate_sip_future_value(kwargs)
            elif calculation_type == "emi":
                return self._calculate_emi(kwargs)
            elif calculation_type == "compound_interest":
                return self._calculate_compound_interest(kwargs)
            elif calculation_type == "xirr":
                return self._calculate_simple_xirr(kwargs)
            else:
                return f"Calculation type '{calculation_type}' not supported"
                
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    def _calculate_sip_future_value(self, params: dict) -> str:
        """Calculate SIP future value"""
        monthly_amount = float(params.get('monthly_amount', 0))
        annual_rate = float(params.get('annual_rate', 12)) / 100
        years = float(params.get('years', 10))
        
        monthly_rate = annual_rate / 12
        months = years * 12
        
        if monthly_rate > 0:
            future_value = monthly_amount * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
        else:
            future_value = monthly_amount * months
            
        return f"SIP Future Value: ₹{future_value:,.2f}"
    
    def _calculate_emi(self, params: dict) -> str:
        """Calculate loan EMI"""
        principal = float(params.get('principal', 0))
        annual_rate = float(params.get('annual_rate', 10)) / 100
        years = float(params.get('years', 20))
        
        monthly_rate = annual_rate / 12
        months = years * 12
        
        if monthly_rate > 0:
            emi = principal * monthly_rate * ((1 + monthly_rate) ** months) / (((1 + monthly_rate) ** months) - 1)
        else:
            emi = principal / months
            
        return f"Monthly EMI: ₹{emi:,.2f}"
    
    def _calculate_compound_interest(self, params: dict) -> str:
        """Calculate compound interest"""
        principal = float(params.get('principal', 0))
        annual_rate = float(params.get('annual_rate', 8)) / 100
        years = float(params.get('years', 10))
        compound_frequency = int(params.get('compound_frequency', 1))
        
        amount = principal * ((1 + annual_rate/compound_frequency) ** (compound_frequency * years))
        interest = amount - principal
        
        return f"Maturity Amount: ₹{amount:,.2f}, Interest Earned: ₹{interest:,.2f}"
    
    def _calculate_simple_xirr(self, params: dict) -> str:
        """Simple XIRR approximation"""
        invested = float(params.get('invested_amount', 0))
        current_value = float(params.get('current_value', 0))
        years = float(params.get('years', 1))
        
        if invested > 0 and years > 0:
            xirr = ((current_value / invested) ** (1/years) - 1) * 100
            return f"Approximate XIRR: {xirr:.2f}%"
        else:
            return "Insufficient data for XIRR calculation"