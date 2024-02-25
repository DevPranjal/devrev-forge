import praw
from datetime import datetime
import json

client_id = "753dHhmqWu6pBEs4mDEs2w"
client_secret = "WmkKW2R0KaEJ84EWMasITlI4rRmxYw"
user_agent = "tachyon-11"


def get_reddit_posts(query, subreddit, k=10):
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         user_agent=user_agent)

    if subreddit:
        subreddit = reddit.subreddit(subreddit)
        submissions = subreddit.search(query=query, sort="new", limit=k)
    else:
        submissions = reddit.search(query=query, sort="new", limit=k)

    result = []
    for s in submissions:
        result.append({
            'title': s.title,
            'url': s.url,
            'upvotes': s.ups,
            'downvotes': s.downs,
            'num_comments': s.num_comments,
            'body': s.selftext,
            'author': s.author.name,
            'created': datetime.utcfromtimestamp(s.created_utc).date()
        })

    return result

if __name__ == "__main__":
    query = "problems"
    subreddit = "Adobe"
    k = 100
    posts = get_reddit_posts(query, subreddit, k)
    
    with open("../data/reddit.json", "w") as final:
        json.dump(posts, final, indent=2)
