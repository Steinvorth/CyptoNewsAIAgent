import requests
from typing import List, Dict
from datetime import datetime
import time
from supabase import create_client, Client
from colorama import init, Fore, Style

init()  # Initialize colorama


class CryptoNewsAnalyzer:
    def __init__(
        self,
        llm_endpoint: str,
        searxng_url: str,
        supabase_url: str,
        supabase_key: str,
        model_name: str = "mistral-nemo-instruct-2407",
    ):
        self.llm_endpoint = llm_endpoint
        self.searxng_url = searxng_url
        self.model_name = model_name
        self.seen_articles = set()  # Track seen articles to avoid duplicates
        self.supabase: Client = create_client(supabase_url, supabase_key)

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
        """Fixed LLM analysis"""
        try:
            prompt = """
            Analyze this crypto content and extract key information:
            {content}

            Return analysis in this EXACT format:
            COINS_MENTIONED: List all cryptocurrency symbols mentioned (Example: DOGE, SHIB)
            SENTIMENT: (Very Bearish/Bearish/Neutral/Bullish/Very Bullish)
            IMPACT: (1-10)
            KEY_POINTS:
            - point 1
            - point 2
            RECOMMENDATION: (Buy/Sell/Hold/Watch)
            CONFIDENCE: (1-10)
            EVALUATION: (Yes/No)
            REASON: (Brief explanation)
            """

            response = requests.post(
                f"{self.llm_endpoint}/v1/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional crypto analyst.",
                        },
                        {"role": "user", "content": prompt.format(content=content)},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
            )

            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    analysis = result["choices"][0]["message"]["content"]
                    return self._parse_analysis(analysis)

            print(f"{Fore.RED}LLM API Error: {response.text}{Style.RESET_ALL}")
            return {}

        except Exception as e:
            print(f"{Fore.RED}Error in analyze_with_llm: {str(e)}{Style.RESET_ALL}")
            return {}

    def _parse_analysis(self, analysis: str) -> Dict:
        """Enhanced analysis parser"""
        try:
            coins_mentioned = []
            if "COINS_MENTIONED:" in analysis:
                coins_section = (
                    analysis.split("COINS_MENTIONED:")[1].split("\n")[0].strip()
                )
                coins_mentioned = [coin.strip() for coin in coins_section.split(",")]

            return {
                "coins_mentioned": coins_mentioned,
                "sentiment": self._extract_field(analysis, "SENTIMENT:"),
                "impact": self._extract_field(analysis, "IMPACT:"),
                "key_points": self._extract_list(analysis, "KEY_POINTS:"),
                "recommendation": self._extract_field(analysis, "RECOMMENDATION:"),
                "confidence": self._extract_field(analysis, "CONFIDENCE:"),
                "evaluation": self._extract_field(analysis, "EVALUATION:"),
                "reason": self._extract_field(analysis, "REASON:"),
                "raw_analysis": analysis,
            }
        except Exception as e:
            print(f"{Fore.RED}Error parsing analysis: {str(e)}{Style.RESET_ALL}")
            return {}

    def _extract_field(self, text: str, field: str) -> str:
        """Helper to extract fields from analysis"""
        try:
            if field in text:
                return text.split(field)[1].split("\n")[0].strip()
            return ""
        except:
            return ""

    def _extract_list(self, text: str, field: str) -> List[str]:
        """Helper to extract lists from analysis"""
        try:
            if field in text:
                section = text.split(field)[1].split("\n\n")[0]
                return [
                    point.strip("- ").strip()
                    for point in section.split("\n")
                    if point.strip()
                ]
            return []
        except:
            return []

    def search_crypto_news(self, query: str, num_results: int = 10) -> List[Dict]:
        """Enhanced search with broader sources"""
        headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}

        # Add more crypto news sources
        params = {
            "q": f"{query} -bitcoin -ethereum site:twitter.com OR site:reddit.com/r/cryptocurrency OR site:coinmarketcap.com OR site:cryptonews.com OR site:cointelegraph.com OR site:decrypt.co OR site:coindesk.com",
            "format": "json",
            "results": num_results,
            "time_range": "day",
        }

        print(f"\n{Fore.CYAN}Searching with query:{Style.RESET_ALL} {params['q']}")
        return self._make_search_request(headers, params)

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

    def discover_trending_coins(self, ignore_evaluation: bool = False) -> Dict:
        promising_coins = {}  # Dict to store coin data and aggregated analysis

        queries = [
            "viral crypto token trending social media",
            "new cryptocurrency listing pump",
            "crypto token price surge today",
            "meme coin trending twitter crypto",
            "altcoin massive gains trading volume",
        ]

        for query in queries:
            print(f"\n{Fore.GREEN}Analyzing Trend Query: {query}{Style.RESET_ALL}")
            news = self.search_crypto_news(query, num_results=5)

            for article in news:
                # First, extract coin names
                coin_extraction_prompt = """
                Analyze this text and extract cryptocurrency names.
                Format each finding as: SYMBOL: FULL_NAME
                Example: "DOGE: Dogecoin"
                Focus on finding the exact trading symbol and full name.
                Only include coins that are specifically mentioned with clear identifiers.
                If no specific coins found, return 'None'

                Text: {content}
                """.format(
                    content=f"{article.get('title')} {article.get('content')}"
                )

                try:
                    response = requests.post(
                        f"{self.llm_endpoint}/v1/chat/completions",
                        json={
                            "model": self.model_name,
                            "messages": [
                                {"role": "user", "content": coin_extraction_prompt}
                            ],
                            "temperature": 0.3,
                        },
                    )

                    coins_text = response.json()["choices"][0]["message"][
                        "content"
                    ].strip()
                    if coins_text.lower() != "none":
                        # For each identified coin, perform detailed analysis
                        for coin_entry in coins_text.split("\n"):
                            if ":" in coin_entry:
                                symbol, name = coin_entry.split(":", 1)
                                symbol = symbol.strip()
                                name = name.strip()

                                # Perform detailed analysis for this specific coin
                                analysis_prompt = f"""
                                Analyze this cryptocurrency: {symbol} ({name})
                                Context: {article.get('content')}

                                Provide detailed analysis:
                                1. SENTIMENT: Rate market sentiment (Very Bearish/Bearish/Neutral/Bullish/Very Bullish)
                                2. IMPACT: Rate potential market impact (1-10)
                                3. KEY POINTS: List main points about this specific coin
                                4. RECOMMENDATION: Clear trading/investment recommendation
                                5. CONFIDENCE: Rate analysis confidence (1-10)
                                6. EVALUATION: Should we monitor this coin? (Yes/No)
                                7. REASON: Specific reasons to monitor or avoid this coin
                                8. RISK_LEVEL: Rate investment risk (Low/Medium/High)
                                9. MARKET_CAP: Mention if discussed
                                10. TRADING_VOLUME: Mention if discussed
                                """

                                analysis = self.analyze_with_llm(analysis_prompt)

                                # Store or update coin analysis
                                if symbol not in promising_coins:
                                    promising_coins[symbol] = {
                                        "symbol": symbol,
                                        "name": name,
                                        "analyses": [],
                                        "total_impact": 0,
                                        "total_confidence": 0,
                                        "mentions": 0,
                                    }

                                promising_coins[symbol]["analyses"].append(analysis)
                                promising_coins[symbol]["mentions"] += 1
                                promising_coins[symbol]["total_impact"] += float(
                                    analysis.get("impact", 0)
                                )
                                promising_coins[symbol]["total_confidence"] += float(
                                    analysis.get("confidence", 0)
                                )

                                # Print analysis report
                                is_promising = (
                                    analysis.get("evaluation", "").lower() == "yes"
                                    and float(analysis.get("impact", 0)) >= 7
                                    and float(analysis.get("confidence", 0)) >= 6
                                )
                                self._print_analysis_report(
                                    f"{symbol} ({name})", analysis, is_promising
                                )

                except Exception as e:
                    print(
                        f"{Fore.RED}Error analyzing article: {str(e)}{Style.RESET_ALL}"
                    )

        # Final analysis and storage
        final_candidates = []
        for symbol, data in promising_coins.items():
            if data["mentions"] >= 2:  # Require multiple mentions
                avg_impact = data["total_impact"] / data["mentions"]
                avg_confidence = data["total_confidence"] / data["mentions"]

                if avg_impact >= 7 and avg_confidence >= 6:
                    best_analysis = max(
                        data["analyses"], key=lambda x: float(x.get("impact", 0))
                    )
                    self.store_coin_in_supabase(data["symbol"], best_analysis)
                    final_candidates.append(
                        {
                            "symbol": data["symbol"],
                            "name": data["name"],
                            "avg_impact": avg_impact,
                            "avg_confidence": avg_confidence,
                            "mentions": data["mentions"],
                            "best_analysis": best_analysis,
                        }
                    )

        # Print final summary
        print("\n" + "=" * 80)
        print(f"{Fore.GREEN}FINAL ANALYSIS SUMMARY{Style.RESET_ALL}")
        print("=" * 80)
        print(f"Total coins analyzed: {len(promising_coins)}")
        print(f"Final candidates selected: {len(final_candidates)}")

        for candidate in final_candidates:
            print(
                f"\n{Fore.YELLOW}{candidate['symbol']}{Style.RESET_ALL} ({candidate['name']})"
            )
            print(f"Average Impact: {candidate['avg_impact']:.2f}/10")
            print(f"Average Confidence: {candidate['avg_confidence']:.2f}/10")
            print(f"Total Mentions: {candidate['mentions']}")
            print(f"Key Points: {candidate['best_analysis'].get('key_points', [])}")

        return {
            "discovery_timestamp": datetime.now().isoformat(),
            "coins_analyzed": len(promising_coins),
            "promising_candidates": final_candidates,
        }

    def store_coin_in_supabase(self, coin_name: str, analysis: Dict) -> None:
        """Store a coin in the Supabase database if it's worth monitoring."""
        data = {
            "coin_name": coin_name,
            "analysis": analysis.get("raw_analysis", ""),
            "sentiment": analysis.get("sentiment", "Unknown"),
            "impact": int(analysis.get("impact", 0)),  # Ensure this is an integer
            "confidence": int(
                analysis.get("confidence", 0)
            ),  # Ensure this is an integer
        }
        try:
            response = self.supabase.table("monitored_coins").insert(data).execute()
            if response.data:
                print(f"Stored {coin_name} in Supabase.")
            else:
                print(f"Failed to store {coin_name} in Supabase: {response}")
        except Exception as e:
            print(f"Error storing {coin_name} in Supabase: {str(e)}")

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

    def _print_analysis_report(
        self, coin: str, analysis: Dict, is_promising: bool = False
    ):
        """Pretty print analysis report to console"""
        print("\n" + "=" * 80)
        print(f"{Fore.CYAN}Analysis Report for: {Fore.YELLOW}{coin}{Style.RESET_ALL}")
        print("=" * 80)

        if is_promising:
            status = f"{Fore.GREEN}PROMISING CANDIDATE{Style.RESET_ALL}"
        else:
            status = f"{Fore.RED}NOT SELECTED{Style.RESET_ALL}"

        print(f"Status: {status}")
        print(
            f"Sentiment: {Fore.BLUE}{analysis.get('sentiment', 'Unknown')}{Style.RESET_ALL}"
        )
        print(f"Impact Score: {analysis.get('impact', '0')}/10")
        print(f"Confidence: {analysis.get('confidence', '0')}/10")
        print("\nKey Points:")
        for point in analysis.get("key_points", []):
            print(f"  • {point}")
        print(
            f"\nRecommendation: {Fore.YELLOW}{analysis.get('recommendation', 'None')}{Style.RESET_ALL}"
        )
        print(f"Reason: {analysis.get('reason', 'None')}")
        print("-" * 80)
