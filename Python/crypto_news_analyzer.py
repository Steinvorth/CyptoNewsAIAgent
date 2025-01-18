import requests
from typing import List, Dict
import json
from datetime import datetime
import time


class CryptoNewsAnalyzer:
    def __init__(
        self,
        llm_endpoint: str,
        searxng_url: str,
        model_name: str = "llama-3.2-3b-instruct",
    ):
        self.llm_endpoint = llm_endpoint
        self.searxng_url = searxng_url
        self.model_name = model_name

    def test_llm_connection(self) -> bool:
        """Test LLM connection and model availability"""
        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": "Say 'LLM connection successful'"}
                ],
                "temperature": 0.7,
                "max_tokens": 50,
            }
            response = requests.post(
                f"{self.llm_endpoint}/v1/chat/completions", json=payload
            )
            return response.status_code == 200
        except Exception as e:
            print(f"LLM connection error: {str(e)}")
            return False

    def analyze_with_llm(self, content: str) -> str:
        """Send content to local LLM for analysis"""
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a crypto market analyst."},
                {
                    "role": "user",
                    "content": f"Analyze this crypto news and provide key insights: {content}",
                },
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }

        response = requests.post(
            f"{self.llm_endpoint}/v1/chat/completions", json=payload
        )
        if response.status_code == 200:
            return (
                response.json()
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
        return ""

    def search_crypto_news(
        self, query: str, num_results: int = 10, max_retries: int = 3
    ) -> List[Dict]:
        """Search for crypto news using SearxNG instance with retry mechanism"""
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        }
        params = {
            "q": query,
            "format": "json",
            "category": "news",
            "results": num_results,
        }

        for attempt in range(max_retries):
            try:
                response = requests.get(
                    self.searxng_url, headers=headers, params=params
                )
                if response.status_code == 429:  # Too Many Requests
                    wait_time = (attempt + 1) * 2
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue

                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
            except Exception as e:
                print(f"Error in search_crypto_news (attempt {attempt+1}): {str(e)}")
                time.sleep(1)
        return []

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
