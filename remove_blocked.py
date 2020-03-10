import pywikibot
import re

if __name__ == "__main__":
    site = pywikibot.Site(fam="wikipedia", code="en", user="TheSandBot")
    pattern = r'(?:User talk:)([^/\n]+)'
    for page in pywikibot.Category(site, "Wikipedia usernames with possible policy issues").articles():
        if page.title() == "Template:Uw-corpname":
            continue
        m = re.search(pattern, str(page.title()))
        user_raw = m.group(1)
        user = pywikibot.User(site, user_raw)
        if user.isBlocked():
            with open("block_removed_mar_9_2020.txt", 'a+') as f:
                f.write(str(page.title()) + "\n")
            page.text = page.text.replace("[[Category:Wikipedia usernames with possible policy issues|{{PAGENAME}}]]",
                                          "")
            page.save(
                summary="Removing [[:Category:Wikipedia usernames with possible policy issues]] as user is blocked." +
                        " ([[Wikipedia:Bots/Requests for approval/TheSandBot 6|BRFA]])", minor=True,
                botflag=True, force=True)
            print("Saved " + str(page.title()))
