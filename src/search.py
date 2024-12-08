from duckduckgo_search import DDGS

def perform_duckduckgo_search(query, result_count=5):
    """
    Perform a web search using DuckDuckGo's DDGS.

    Parameters:
        query (str): Search query string.
        result_count (int): Number of results to retrieve.

    Returns:
        list: A list of dictionaries containing search results (title, link, snippet).
    """
    results = []
    with DDGS() as ddgs:
        for result in ddgs.text(query, max_results=result_count):
            results.append({
                "title": result.get("title", "No Title"),
                "link": result.get("href", "No Link"),
                "snippet": result.get("body", "No Snippet")
            })
    return results


# Example usage
if __name__ == "__main__":
    query = "Latest advancements in AI"
    try:
        search_results = perform_duckduckgo_search(query, result_count=5)
        for idx, result in enumerate(search_results, start=1):
            print(f"{idx}. {result['title']}")
            print(f"   Link: {result['link']}")
            print(f"   Snippet: {result['snippet']}\n")
    except Exception as e:
        print(f"Error: {e}")
