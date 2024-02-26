import requests

api_key = "apikey"

def get_news(query, k):
    url = f"https://newsapi.org/v2/top-headlines?q={query}&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if data["status"] == "ok":
            result =  data["articles"][:k]
        else:
            return data["message"]
    else:
        return f"API request failed with status code {response.status_code}"
    
    return result

if __name__ == "__main__":
    query = "python"
    k = 10
    posts = get_news(query, k)
    for post in posts:
        print(post.keys())