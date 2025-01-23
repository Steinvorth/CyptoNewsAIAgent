from crewai import Agent
import requests
from typing import Dict


class CoinAnalyzer:
    def __init__(self, llm_endpoint: str):
        self.agent = Agent(
            role="Coin Analysis Specialist",
            goal="Analyze cryptocurrencies for investment potential",
            backstory="Expert cryptocurrency analyst with deep market understanding",
            verbose=True,
        )
        self.llm_endpoint = llm_endpoint

    async def analyze_coin(self, content: str) -> Dict:
        """Analyze specific coin mentions"""
        prompt = """
        Analyze this cryptocurrency content:
        {content}
        
        Provide:
        1. SYMBOL
        2. SENTIMENT (Bullish/Bearish/Neutral)
        3. IMPACT (1-10)
        4. KEY_POINTS
        5. RECOMMENDATION
        """

        response = requests.post(
            self.llm_endpoint,
            json={
                "model": "mistral-nemo-instruct-2407",
                "messages": [
                    {"role": "user", "content": prompt.format(content=content)}
                ],
            },
        )

        return (
            response.json()["choices"][0]["message"]["content"]
            if response.status_code == 200
            else {}
        )
