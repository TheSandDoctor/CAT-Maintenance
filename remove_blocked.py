import pywikibot
import re

if __name__ == "__main__":
    site = pywikibot.Site(fam="wikipedia", code="en", user="TheSandBot")
    pattern = r'(?:User talk:)([^/\n]+)'
    for page in pywikibot.Category(site, "Wikipedia usernames with possible policy issues").articles():
        m = re.search(pattern, str(page.title()))
        user_raw = m.group(1)
        user = pywikibot.User(site, user_raw)
        if user.isBlocked():
            # TODO: remove
            page.text = page.text.replace("[[Category:Wikipedia usernames with possible policy issues|{{PAGENAME}}]]",
                                          "")
            page.save(
                summary="Removing [[:Category:Wikipedia usernames with possible policy issues]] as user is blocked." +
                        " ([[Wikipedia:Bots/Requests for approval/TheSandBot 6|BRFA]])", minor=True,
                botflag=True, force=True)
            print("Saved " + str(page.title()))
