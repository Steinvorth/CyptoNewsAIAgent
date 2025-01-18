import requests
from typing import List, Dict
from datetime import datetime
import time


class CryptoNewsAnalyzer:
    def __init__(
        self,
        llm_endpoint: str,
        searxng_url: str,
        model_name: str = "mistral-nemo-instruct-2407",
    ):
        self.llm_endpoint = llm_endpoint
        self.searxng_url = searxng_url
        self.model_name = model_name
        self.seen_articles = set()  # Track seen articles to avoid duplicates

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

    def analyze_with_llm(self, content: str) -> Dict:
        """Enhanced LLM analysis with structured output"""
        prompt = """Analyze this crypto news as an expert analyst. Provide:
1. SENTIMENT: Rate market sentiment (Very Bearish, Bearish, Neutral, Bullish, Very Bullish)
2. IMPACT: Rate potential market impact (1-10)
3. KEY POINTS: List main points affecting the crypto market
4. RECOMMENDATION: Provide trading suggestion
5. CONFIDENCE: Rate analysis confidence (1-10)

News content: {content}"""

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional crypto market analyst focused on accurate, data-driven analysis.",
                },
                {"role": "user", "content": prompt.format(content=content)},
            ],
            "temperature": 0.7,
            "max_tokens": 800,
        }

        response = requests.post(
            f"{self.llm_endpoint}/v1/chat/completions", json=payload
        )
        if response.status_code == 200:
            analysis = (
                response.json()
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            return self._parse_analysis(analysis)
        return {}

    def _parse_analysis(self, analysis: str) -> Dict:
        """Parse LLM analysis into structured format"""
        return {
            "sentiment": (
                analysis.split("SENTIMENT:")[1].split("\n")[0].strip()
                if "SENTIMENT:" in analysis
                else "Unknown"
            ),
            "impact": (
                analysis.split("IMPACT:")[1].split("\n")[0].strip()
                if "IMPACT:" in analysis
                else "0"
            ),
            "key_points": (
                analysis.split("KEY POINTS:")[1]
                .split("RECOMMENDATION:")[0]
                .strip()
                .split("\n")
                if "KEY POINTS:" in analysis
                else []
            ),
            "recommendation": (
                analysis.split("RECOMMENDATION:")[1].split("CONFIDENCE:")[0].strip()
                if "RECOMMENDATION:" in analysis
                else ""
            ),
            "confidence": (
                analysis.split("CONFIDENCE:")[1].strip()
                if "CONFIDENCE:" in analysis
                else "0"
            ),
            "raw_analysis": analysis,
        }

    def search_crypto_news(self, query: str, num_results: int = 10) -> List[Dict]:
        """Enhanced crypto news search"""
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        }

        # Simplified search parameters
        params = {
            "q": f"{query} cryptocurrency",
            "format": "json",
            "results": num_results,
        }

        print(f"Searching SearxNG with query: {query}")  # Debugging
        response = requests.get(self.searxng_url, headers=headers, params=params)
        print(f"Response status code: {response.status_code}")  # Debugging
        print(f"Response content: {response.text}")  # Debugging

        if response.status_code == 200:
            return response.json().get("results", [])
        return []

    def get_crypto_insights(self, cryptocurrency: str) -> Dict:
        """Get comprehensive crypto analysis"""
        search_queries = [
            f"{cryptocurrency} price analysis",
            f"{cryptocurrency} market news",
            f"{cryptocurrency} trading volume",
            f"{cryptocurrency} development updates",
        ]

        all_insights = []
        for query in search_queries:
            news = self.search_crypto_news(query, num_results=3)
            for article in news:
                if article["url"] not in self.seen_articles:  # Avoid duplicates
                    self.seen_articles.add(article["url"])
                    analysis = self.analyze_with_llm(article.get("content", ""))
                    if analysis:
                        all_insights.append(
                            {
                                "title": article.get("title"),
                                "url": article.get("url"),
                                "timestamp": datetime.now().isoformat(),
                                "analysis": analysis,
                            }
                        )

        return {
            "cryptocurrency": cryptocurrency,
            "analysis_timestamp": datetime.now().isoformat(),
            "total_articles": len(all_insights),
            "insights": all_insights,
            "summary": self._generate_summary(all_insights),
        }

    def _generate_summary(self, insights: List[Dict]) -> Dict:
        """Generate summary of all insights"""
        if not insights:
            return {}

        sentiment_scores = {
            "Very Bullish": 2,
            "Bullish": 1,
            "Neutral": 0,
            "Bearish": -1,
            "Very Bearish": -2,
        }
        sentiments = [insight["analysis"].get("sentiment") for insight in insights]
        impacts = [float(insight["analysis"].get("impact", 0)) for insight in insights]

        avg_sentiment = sum(sentiment_scores.get(s, 0) for s in sentiments) / len(
            sentiments
        )
        avg_impact = sum(impacts) / len(impacts) if impacts else 0

        return {
            "overall_sentiment": (
                "Bullish"
                if avg_sentiment > 0
                else "Bearish" if avg_sentiment < 0 else "Neutral"
            ),
            "sentiment_score": round(avg_sentiment, 2),
            "average_impact": round(avg_impact, 2),
            "analysis_count": len(insights),
        }
