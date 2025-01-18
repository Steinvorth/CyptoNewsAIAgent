from flask import Flask, jsonify, request
from crypto_news_analyzer import CryptoNewsAnalyzer
import time

app = Flask(__name__)

# Initialize the analyzer
analyzer = CryptoNewsAnalyzer(
    llm_endpoint="http://127.0.0.1:1234/v1/completions",  # Updated LM Studio endpoint
    searxng_url="http://132.145.130.5:8080/search",  # Your SearxNG instance
)


@app.route("/api/analyze", methods=["GET"])
def analyze_crypto():
    """
    Analyze a specific cryptocurrency.
    Query parameter: crypto (e.g., Bitcoin)
    """
    cryptocurrency = request.args.get("crypto", "Bitcoin")
    insights = analyzer.get_crypto_insights(cryptocurrency)
    return jsonify(insights)


@app.route("/api/monitor", methods=["GET"])
def monitor_crypto():
    """
    Continuously monitor for new crypto news.
    Query parameter: crypto (e.g., Bitcoin)
    """
    cryptocurrency = request.args.get("crypto", "Bitcoin")
    while True:
        insights = analyzer.get_crypto_insights(cryptocurrency)
        if insights["total_articles"] > 0:
            return jsonify(insights)
        time.sleep(300)  # Wait 5 minutes before checking again


@app.route("/api/search", methods=["GET"])
def search_crypto():
    """
    Search for crypto news based on a query.
    Query parameters: query (e.g., "meme coins"), num_results (e.g., 10)
    """
    query = request.args.get("query", "meme coins")
    num_results = int(request.args.get("num_results", 10))
    news = analyzer.search_crypto_news(query, num_results)
    return jsonify(news)


@app.route("/api/discover", methods=["GET"])
def discover_trending_coins():
    """
    Discover trending coins and news by searching for general crypto news.
    """
    insights = analyzer.discover_trending_coins()
    return jsonify(insights)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
