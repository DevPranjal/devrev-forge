import requests
import json

def get_hackernews_posts(query, k=10):
    search_url = f"https://hn.algolia.com/api/v1/search_by_date?tags=story&query={query}"
    response = requests.get(search_url)

    if response.status_code == 200:
        data = json.loads(response.content)
        posts = data["hits"][:k]

        result = []
        for p in posts:
            result.append({
                "title": p["title"],
                "url": p.get("url", ""),
                "author": p["author"],
                "created_at": p["created_at"],
                "points": p["points"],
                "num_comments": p["num_comments"],
                "content": p.get("story_text", "")
            })

            return result

    else:
        print(f"Error: API request failed with status code {response.status_code}")
        return []

if __name__ == "__main__":
    query = "adobe"
    k = 1000
    posts = get_hackernews_posts(query, k)

    with open("../data/hackernews.json", "w") as f:
        json.dump(posts, f, indent=2)