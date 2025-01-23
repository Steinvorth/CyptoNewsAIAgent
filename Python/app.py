from flask import Flask, jsonify, request
from crypto_news_analyzer import CryptoNewsAnalyzer
import time

app = Flask(__name__)

# Initialize the analyzer
analyzer = CryptoNewsAnalyzer(
    llm_endpoint="http://127.0.0.1:1234/v1/chat/completions",  # Updated endpoint
    searxng_url="http://132.145.130.5:8080/search",  # Your SearxNG instance
    supabase_url="https://ejrtiiqnprwzmyzoemjh.supabase.co",  # Supabase URL
    supabase_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVqcnRpaXFucHJ3em15em9lbWpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcyMjk5ODYsImV4cCI6MjA1MjgwNTk4Nn0.io8MKZAlmuAGKBMBd_PbpxIpD5y4ztRV2wcJowLVd4Y",  # Supabase anon key
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


# Using the API endpoint
@app.route("/api/discover", methods=["GET"])
@app.route("/api/discover/<eval_mode>", methods=["GET"])
def discover_trending_coins(eval_mode=None):
    try:
        print(f"Received discover request with eval_mode: {eval_mode}")  # Debug logging
        ignore_evaluation = eval_mode == "false"
        insights = analyzer.discover_trending_coins(ignore_evaluation=ignore_evaluation)
        print(f"Generated insights: {insights}")  # Debug logging
        return jsonify(insights)
    except Exception as e:
        print(f"Error in discover_trending_coins: {str(e)}")  # Error logging
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001, host="0.0.0.0")  # Enable external access
