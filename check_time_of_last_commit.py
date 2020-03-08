import pywikibot
import re

if __name__ == "__main__":
    site = pywikibot.Site(fam="wikipedia", code="en", user="TheSandBot")
    #count = 0
    pattern = r'(?:User talk:)([^/\n]+)'
    for page in pywikibot.Category(site, "Wikipedia usernames with possible policy issues").articles():
        print(str(page.latest_revision.timestamp) +" " + page.title())
        m = re.search(pattern, str(page.title()))
        user_raw = m.group(1)
        user = pywikibot.User(site, user_raw)
        #user = pywikibot.User(site, str(page.title()[10:]))
        if int(str(page.latest_revision.timestamp)[0:4]) >= 2020:
            if not user.isBlocked():
                print(str(page.title()))
                with open("2020.txt", 'a+') as f:
                    f.write(str(page.title()) + " :: " + str(page.latest_revision.timestamp) + "\n")
        #if user.isBlocked():
        #    with open("removed.txt", 'a+') as f:
        #        f.write(user.username + "\n")
        #    count += 1