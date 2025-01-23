from crewai import Agent
from typing import Dict


class RiskAnalyzer:
    def __init__(self):
        self.agent = Agent(
            role="Risk Assessment Specialist",
            goal="Evaluate investment risks and market volatility",
            backstory="Expert at crypto risk analysis and market assessment",
            verbose=True,
        )

    async def assess_risks(self, coin_data: Dict) -> Dict:
        """Assess risks for a given coin"""
        risk_factors = {
            "market_risk": self._calculate_market_risk(coin_data),
            "volatility_risk": self._calculate_volatility(coin_data),
            "liquidity_risk": self._assess_liquidity(coin_data),
            "technical_risk": self._assess_technical_factors(coin_data),
        }

        return {
            "overall_risk_score": sum(risk_factors.values()) / len(risk_factors),
            "risk_breakdown": risk_factors,
            "recommendation": self._generate_recommendation(risk_factors),
        }

    def _calculate_market_risk(self, data: Dict) -> float:
        return float(data.get("impact", 5)) / 10

    def _calculate_volatility(self, data: Dict) -> float:
        return float(data.get("confidence", 5)) / 10

    def _assess_liquidity(self, data: Dict) -> float:
        return 0.7  # Default medium-high liquidity risk

    def _assess_technical_factors(self, data: Dict) -> float:
        return 0.5  # Default moderate technical risk

    def _generate_recommendation(self, risk_factors: Dict) -> str:
        avg_risk = sum(risk_factors.values()) / len(risk_factors)
        if avg_risk > 0.7:
            return "High Risk - Careful Consideration Required"
        elif avg_risk > 0.4:
            return "Medium Risk - Monitor Closely"
        return "Low Risk - Standard Precautions"
