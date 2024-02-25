# pip install google-play-scraper
# pip install app-store-scraper

from google_play_scraper import Sort, reviews, reviews_all
from app_store_scraper import AppStore
import json
import datetime

def get_playstore_reviews(appname, k):
    result = reviews_all(
        appname,
        lang='en', # defaults to 'en'
        country='us', # defaults to 'us'
        sort=Sort.NEWEST, # defaults to Sort.NEWEST
        # count=k, # defaults to 100
        filter_score_with=None
    )

    final = []

    for r in result:
        final.append({
            'source': 'google',
            'username': r['userName'],
            'score': r['score'],
            'at': r['at'].date(),
            'content': r['content']
        
        })

    return final

def get_appstore_reviews(appname, appid, k):
    app = AppStore(country="us", app_name=appname, app_id=appid, )
    app.review()
    result = app.reviews
    final = []

    for r in result:
        final.append({
            'source': 'apple',
            'username': r['userName'],
            'score': r['rating'],
            'at': r['date'].date(),
            'content': r['review']
        })

    return final

if __name__ == "__main__":
    appstore_appname = "adobe-acrobat-reader-edit-pdf"
    appstore_appid = 469337564
    playstore_appname = "com.adobe.reader"

    k = 1000
    playstore_reviews = get_playstore_reviews(playstore_appname, k)
    appstore_reviews = get_appstore_reviews(appstore_appname, appstore_appid, k)

    playstore_reviews.extend(appstore_reviews)

    with open("../data/store.json", "w") as final:
        json.dump(playstore_reviews, final, indent=2)