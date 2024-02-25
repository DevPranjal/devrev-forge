import requests
import json
import datetime

url = "https://twitter154.p.rapidapi.com/search/search"


headers = {
	"X-RapidAPI-Key": "084fc27d04msh9d18efbcb36d873p1d4dfbjsn04b89bae060c",
	"X-RapidAPI-Host": "twitter154.p.rapidapi.com"
}

def get_twitter_posts(query, since=""):
    querystring = {
        "query": query,
        "section":"top",
        "min_retweets":"0",
        "min_likes":"0",
        "limit":"10",
        "start_date":since,
        "language":"en"
    }
    
    response = requests.get(url, headers=headers, params=querystring)

    result = []
    for i in response.json()['results']:
        temp = {"creation_date": "", "text":"", "location":"", "favorite_count":0, "retweet_count":0, "reply_count":0, "views":0,}
        temp["text"] = i["text"]
        temp["creation_date"] = datetime.datetime.strptime(i["creation_date"], "%a %b %d %H:%M:%S %z %Y").date()
        temp["location"] = i["user"]["location"]
        temp["retweet_count"] = i["retweet_count"]
        temp["reply_count"] = i["reply_count"]
        temp["views"] = i["views"]


        print(temp["creation_date"])
        result.append(temp)

    return result
