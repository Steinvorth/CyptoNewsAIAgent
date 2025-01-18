from crypto_news_analyzer import CryptoNewsAnalyzer
import json


def test_search():
    print("1. Initializing CryptoNewsAnalyzer...")
    analyzer = CryptoNewsAnalyzer(
        llm_endpoint="http://127.0.0.1:1234",
        searxng_url="http://132.145.130.5:8080/search",
        model_name="llama-3.2-3b-instruct",
    )

    print("\n2. Testing LLM connection...")
    if not analyzer.test_llm_connection():
        print("Error: LLM connection failed. Please check if LM Studio is running.")
        return

    print("\n3. Testing SearxNG connection...")
    news = analyzer.search_crypto_news("Bitcoin latest news", num_results=3)

    if not news:
        print(
            "Error: No results from SearxNG. Check if the search endpoint is working."
        )
        return

    print(f"Success: Found {len(news)} articles")

    print("\n=== Full Results ===")
    for item in news:
        print("\nArticle:")
        print(f"Title: {item.get('title')}")
        print(f"URL: {item.get('url')}")
        print(f"Content Preview: {item.get('content', '')[:100]}...")

        analysis = analyzer.analyze_with_llm(item.get("content", ""))
        if analysis:
            print(f"\nAI Analysis: {analysis[:200]}...")


if __name__ == "__main__":
    test_search()
