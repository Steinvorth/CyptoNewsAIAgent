import time
import requests
from openai import OpenAI

# ============================================
# Part 1: LM Studio Integration
# ============================================


def test_lm_studio():
    print("1. Testing LM Studio connection...")

    # Initialize the OpenAI client for LM Studio
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

    # Define the chat history
    history = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, introduce yourself."},
    ]

    try:
        # Send a completion request to LM Studio
        completion = client.chat.completions.create(
            model="model-identifier",  # Replace with your model's identifier
            messages=history,
            temperature=0.7,
            stream=True,
        )

        # Print the assistant's response
        print("LM Studio Response:")
        for chunk in completion:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"Error connecting to LM Studio: {e}")


# ============================================
# Part 2: SearxNG Web Scraping
# ============================================


def search_searxng(query, num_results=3):
    """
    Searches a SearxNG instance for the given query.
    """
    searxng_url = (
        "http://132.145.130.5:8080/search"  # Replace with your SearxNG instance URL
    )
    params = {
        "q": query,
        "format": "json",
        "language": "en",
        "safesearch": 1,
        "num": num_results,
    }

    try:
        response = requests.get(searxng_url, params=params)
        if response.status_code == 200:
            results = response.json().get("results", [])
            return results
        else:
            print(f"Error: Status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def search_with_retry(query, num_results=3, retries=3):
    """
    Searches SearxNG with retries and exponential backoff.
    """
    for attempt in range(retries):
        results = search_searxng(query, num_results)
        if results:
            return results
        else:
            wait_time = 2 ** (attempt + 1)  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
    return None


def test_searxng():
    print("\n2. Testing SearxNG connection...")

    # Example query
    query = "Bitcoin latest news"
    results = search_with_retry(query, num_results=3)

    if results:
        print(f"Success: Found {len(results)} articles")
        print("\n=== Full Results ===")
        for item in results:
            print("\nArticle:")
            print(f"Title: {item.get('title')}")
            print(f"URL: {item.get('url')}")
            print(f"Content Preview: {item.get('content', '')[:100]}...")
    else:
        print(
            "Error: No results from SearxNG. Check if the search endpoint is working."
        )


# ============================================
# Main Function
# ============================================

if __name__ == "__main__":
    # Test LM Studio
    test_lm_studio()

    # Test SearxNG
    test_searxng()
