import requests
from typing import List, Dict
import json
from datetime import datetime


class CryptoNewsAnalyzer:
    def __init__(self, llm_endpoint: str, searxng_url: str):
        self.llm_endpoint = llm_endpoint
        self.searxng_url = searxng_url

    def search_crypto_news(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search for crypto news using SearxNG instance"""
        headers = {"Accept": "application/json"}
        params = {
            "q": query,
            "format": "json",
            "category": "news",
            "results": num_results,
        }

        response = requests.get(self.searxng_url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get("results", [])
        return []

    def analyze_with_llm(self, content: str) -> str:
        """Send content to local LLM for analysis"""
        payload = {
            "prompt": f"Analyze this crypto news and provide key insights: {content}",
            "max_tokens": 500,
            "temperature": 0.7,
        }

        response = requests.post(self.llm_endpoint, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "")
        return ""

    def get_crypto_insights(self, cryptocurrency: str) -> Dict:
        """Main method to get and analyze crypto news"""
        news = self.search_crypto_news(f"{cryptocurrency} cryptocurrency news")

        insights = []
        for article in news:
            analysis = self.analyze_with_llm(article.get("content", ""))
            if analysis:
                insights.append(
                    {
                        "title": article.get("title"),
                        "url": article.get("url"),
                        "analysis": analysis,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return {
            "cryptocurrency": cryptocurrency,
            "total_articles": len(news),
            "insights": insights,
        }


def main():
    analyzer = CryptoNewsAnalyzer(
        llm_endpoint="http://127.0.0.1:1234/v1/completions",  # Updated LM Studio endpoint
        searxng_url="http://132.145.130.5:8080/search",  # Your SearxNG instance
    )

    results = analyzer.get_crypto_insights("Bitcoin")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
