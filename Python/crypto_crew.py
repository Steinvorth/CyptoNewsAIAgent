from crewai import Crew, Process, Agent
from agents.news_scanner import NewsScanner
from agents.coin_analyzer import CoinAnalyzer
from agents.trend_spotter import TrendSpotter
from agents.risk_analyzer import RiskAnalyzer
from agents.sentiment_analyzer import SentimentAnalyzer
from typing import Dict, List
from datetime import datetime
from flask import Flask, jsonify, request
from crypto_news_analyzer import CryptoNewsAnalyzer
import asyncio
from functools import wraps

app = Flask(__name__)
analyzer = CryptoNewsAnalyzer()


def async_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


class CryptoCrew:
    def __init__(self, config: Dict):
        self.news_scanner = NewsScanner(config["searxng_url"])
        self.coin_analyzer = CoinAnalyzer(config["llm_endpoint"])
        self.trend_spotter = TrendSpotter()
        self.risk_analyzer = RiskAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer(config["llm_endpoint"])

    async def analyze_market(self) -> Dict:
        """Coordinate market analysis tasks"""
        # 1. Scan for news
        news_data = await self.news_scanner.scan_news("trending cryptocurrency")

        # 2. Analyze trends
        trends = await self.trend_spotter.analyze_trends(news_data)

        # 3. For each potential coin
        coin_analyses = []
        for article in news_data:
            # Analyze the coin
            coin_analysis = await self.coin_analyzer.analyze_coin(article["content"])

            # Assess risks
            risk_assessment = await self.risk_analyzer.assess_risks(coin_analysis)

            # Analyze sentiment
            sentiment = await self.sentiment_analyzer.analyze_sentiment(
                article["content"]
            )

            if self._is_promising_candidate(coin_analysis, risk_assessment, sentiment):
                coin_analyses.append(
                    {
                        "coin_data": coin_analysis,
                        "risk_assessment": risk_assessment,
                        "sentiment": sentiment,
                    }
                )

        return self.compile_results(coin_analyses, trends)

    def _is_promising_candidate(
        self, analysis: Dict, risk: Dict, sentiment: Dict
    ) -> bool:
        """Determine if a coin is a promising candidate"""
        return (
            float(analysis.get("impact", 0)) >= 7
            and float(analysis.get("confidence", 0)) >= 6
            and risk["overall_risk_score"] <= 0.7
            and sentiment["confidence"] >= 7
        )

    def compile_results(self, coin_analyses: List[Dict], trends: Dict) -> Dict:
        """Compile all agent results"""
        return {
            "coins_analyzed": len(coin_analyses),
            "promising_candidates": [
                analysis
                for analysis in coin_analyses
                if self._is_promising_candidate(
                    analysis["coin_data"],
                    analysis["risk_assessment"],
                    analysis["sentiment"],
                )
            ],
            "market_trends": trends,
            "timestamp": datetime.now().isoformat(),
        }

    def _make_search_request(self, headers: Dict, params: Dict) -> List[Dict]:
        """Make search request to SearxNG"""
        try:
            response = requests.get(self.searxng_url, headers=headers, params=params)
            if response.status_code == 200:
                results = response.json().get("results", [])
                print(f"\n{Fore.GREEN}Found {len(results)} articles{Style.RESET_ALL}")

                # Print article details
                for result in results:
                    print(f"\n{Fore.YELLOW}Found Article:{Style.RESET_ALL}")
                    print(f"Title: {result.get('title')}")
                    print(f"Content: {result.get('content', '')[:200]}...")

                return results
            print(
                f"{Fore.RED}Search failed with status: {response.status_code}{Style.RESET_ALL}"
            )
            return []
        except Exception as e:
            print(f"{Fore.RED}Search error: {str(e)}{Style.RESET_ALL}")
            return []


@app.route("/api/discover", methods=["GET"])
@app.route("/api/discover/<eval_mode>", methods=["GET"])
@async_route
async def discover_trending_coins(eval_mode=None):
    try:
        print(f"Received discover request with eval_mode: {eval_mode}")
        ignore_evaluation = eval_mode == "false"
        insights = await analyzer.discover_trending_coins(
            ignore_evaluation=ignore_evaluation
        )
        print(f"Generated insights: {insights}")
        return jsonify(insights)
    except Exception as e:
        print(f"Error in discover_trending_coins: {str(e)}")
        return jsonify({"error": str(e)}), 500
