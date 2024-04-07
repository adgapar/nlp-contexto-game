import os
import requests
import json
from collections import Counter
from datetime import datetime


API_KEY = os.environ["NEWS_API_TOKEN"]

def get_news_from_api():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}"
    response = requests.get(url)
    response_json = response.json()
    if response_json["status"] == "error":
        return []
    
    articles = response_json["articles"]
    return articles

def get_today_news():
    today = datetime.today()
    week_number = today.isocalendar()[1]
    
    try:
        with open(f"words_week_{week_number}.json") as f:
            words_dict = json.load(f)
            return words_dict
    except FileNotFoundError:
        words_dict = {}
        articles = get_news_from_api()
        for article in articles:
            content = article["content"]
            if content is None:
                continue
            
            words = content.split()
            words_counter = Counter(words)
            if not words_dict:
                words_dict = words_counter
            else:
                words_dict += words_counter

        if not words_dict:
            raise ValueError("No news available")

        with open(f"words_week_{week_number}.json", "w") as f:
            json.dump(words_dict, f)

        return words_dict


