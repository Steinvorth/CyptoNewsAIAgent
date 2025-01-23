from crewai import Agent
import requests
from typing import List, Dict


class NewsScanner:
    def __init__(self, searxng_url: str):
        self.agent = Agent(
            role="Crypto News Scanner",
            goal="Find and filter relevant cryptocurrency news",
            backstory="Expert at discovering emerging crypto trends and news",
            verbose=True,
        )
        self.searxng_url = searxng_url

    async def scan_news(self, query: str) -> List[Dict]:
        """Scan crypto news sources"""
        headers = {"Accept": "application/json"}
        params = {
            "q": f"{query} site:cryptonews.com OR site:cointelegraph.com OR site:coindesk.com",
            "format": "json",
            "time_range": "day",
        }

        response = requests.get(self.searxng_url, headers=headers, params=params)
        return response.json().get("results", []) if response.status_code == 200 else []
