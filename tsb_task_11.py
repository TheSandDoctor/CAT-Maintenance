import pywikibot
import requests
from datetime import datetime

class SwapCategories:

    def __init__(self, category_name, site):
        self.category_name = category_name
        self.site = site
        self.edit_count = 0
        self.max_edits = 5
        self.BASE_URL = "https://en.wikipedia.org/w/api.php"

    def get_formatted_timestamp(self, timestamp):
        return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ').strftime('%B %Y')

    def update_page_category(self, member):
        timestamp = self.get_formatted_timestamp(member['timestamp'])
        page = pywikibot.Page(self.site, member['title'])
        text = page.text
        old_category = '[[Category:Wikipedia usernames with possible policy issues]]'
        new_category = f'[[Category:Wikipedia usernames with possible policy issues from {timestamp}]]'
        
        if old_category in text:
            text = text.replace(old_category, new_category)
            page.text = text
            page.save(f"Moved from 'Wikipedia usernames with possible policy issues' to 'Category:Wikipedia usernames with possible policy issues from {timestamp}'")
            self.edit_count += 1

    def run_bot(self):
        PARAMS = {
            "action": "query",
            "format": "json",
            "list": "categorymembers",
            "cmtitle": self.category_name,
            "cmprop": "ids|title|timestamp",
            "cmnamespace": "3",
            "cmsort": "timestamp",
            "cmdir": "newer",
            "cmlimit": "500"
        }
        
        while self.edit_count < self.max_edits:
            response = requests.get(self.BASE_URL, params=PARAMS)
            data = response.json()
            members = data.get('query', {}).get('categorymembers', [])
            
            for member in members:
                if self.edit_count >= self.max_edits:
                    return
                self.update_page_category(member)
            
            if 'continue' in data and 'cmcontinue' in data['continue']:
                PARAMS['cmcontinue'] = data['continue']['cmcontinue']
            else:
                break


if __name__ == "__main__":
    # Initialize the site object for English Wikipedia.
    site = pywikibot.Site("en", "wikipedia")
    bot = SwapCategories("Category:Wikipedia usernames with possible policy issues", site)
    bot.run_bot()
