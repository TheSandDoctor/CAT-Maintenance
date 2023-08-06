import pywikibot
import requests
from datetime import datetime
from collections import Counter

BASE_URL = "https://en.wikipedia.org/w/api.php"
timestamp_counts = Counter()

def get_timestamps_from_category(category_name):
    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category_name,
        "cmprop": "ids|title|timestamp",
        "cmnamespace": "3",
        "cmsort": "timestamp",
        "cmdir": "newer",
        "cmlimit": "500"  # Fetch up to 500 results; adjust as needed
    }
    
    while True:
        response = requests.get(BASE_URL, params=PARAMS)
        data = response.json()
        
        members = data.get('query', {}).get('categorymembers', [])
        
        for member in members:
            timestamp = member['timestamp']
            formatted_timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ').strftime('%B %Y')
            timestamp_counts[formatted_timestamp] += 1
            print(member['title'], formatted_timestamp)

        # If 'continue' field exists in the response, set the 'cmcontinue' parameter for the next request
        if 'continue' in data and 'cmcontinue' in data['continue']:
            PARAMS['cmcontinue'] = data['continue']['cmcontinue']
        else:
            break  # If there's no 'continue' field, break the loop

def display_counts():
    for month_year, count in timestamp_counts.items():
        print(f"{month_year}: {count} occurrences")
# Fetch timestamps for members of the specified category
get_timestamps_from_category("Category:Wikipedia usernames with possible policy issues")
display_counts()
