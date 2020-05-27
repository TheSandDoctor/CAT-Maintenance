import pywikibot
import re
import requests


class RemoveBase:
    def __init__(self, log_name, category, trial = False):
        self.pattern = r'(?:User talk:)([^/\n]+)'
        self.site = pywikibot.Site()  # fam="wikipedia", code="en", user="TheSandBot")
        self.count = 0
        self.log_filename = log_name
        self.session = requests.Session()
        try:
            self.category = pywikibot.Category(self.site, category).articles()
        except pywikibot.InvalidTitle:
            print("\nBad category title")
            exit()
        self.cat_name = category
        self.trial = trial

    def category_remove(self, target: str, page: pywikibot.Page) -> None:
        """

        :param target: Target category to remove
        :param page: page object to edit
        :return: None
        """
        page.text = page.text.replace(target, "")

    def generate_user(self, page: pywikibot.Page) -> pywikibot.User:
        m = re.search(self.pattern, str(page.title()))
        user_raw = m.group(1)
        return pywikibot.User(self.site, user_raw)

    def isLocked(self, username):
        params = {
            "action": "query",
            "format": "json",
            "meta": "globaluserinfo",
            "guiuser": str(username),
            "guiprop": "groups|merged|unattached"
        }
        result = self.session.get(url="https://en.wikipedia.org/w/api.php", params=params)
        return 'locked' in result.json()["query"]["globaluserinfo"]

    def log(self, page):
        with open(self.log_filename, 'a+') as f:
            # self.count += 1
            f.write(str(page.title()) + "\n")


class RemoveBlocked(RemoveBase):
    def __init__(self, log_name, category, target, brfa, trial=False, count=50):
        super(RemoveBlocked, self).__init__(log_name, category, trial)
        self.target = target
        self.brfa = brfa
        if trial:
            self.count = count

    def run(self):
        counter = 0
        for page in self.category:
            if page.title() == "Template:Uw-corpname":
                continue
            if counter >= self.count:
                print("\n\nDONE TRIAL\n\n")
                return
            try:
                user = self.generate_user(page)
            except AttributeError:
                print("Failed" + page.title())
                continue
            summary = "Removing [[Category:" + self.cat_name + "]] as user is "
            #print(user.username)
            try:
                if self.isLocked(user.username):
                    self.log(page)
                    self.category_remove(self.target, page)
                    page.save(
                        summary=summary + "locked." +
                                " ([[Wikipedia:Bots/Requests for approval/" + self.brfa + "|BRFA]])", minor=True,
                        botflag=True, force=True)
                    print("Saved " + str(page.title()))
                    if self.trial:
                        counter += 1
                        print(counter)
                elif user.isBlocked():
                    self.log(page)
                    self.category_remove(self.target, page)
                    page.save(
                        summary=summary + "blocked." +
                                " ([[Wikipedia:Bots/Requests for approval/" + self.brfa + "|BRFA]])", minor=True,
                        botflag=True, force=True)
                    print("Saved " + str(page.title()))
                    if self.trial:
                        counter += 1
                        print(counter)
            except KeyError:
                print("No global account")
                if user.isBlocked():
                    self.log(page)
                    self.category_remove(self.target, page)
                    page.save(
                        summary=summary + "blocked." +
                                " ([[Wikipedia:Bots/Requests for approval/" + self.brfa + "|BRFA]])", minor=True,
                        botflag=True, force=True)
                    print("Saved " + str(page.title()))
                    if self.trial:
                        counter += 1
                        print(counter)


class RemoveUnblocked(RemoveBase):
    def __init__(self, log_name, category, target, backup_target, brfa, trial = False):
        super(RemoveUnblocked, self).__init__(log_name, category, trial)
        self.target = target
        self.backup_target = backup_target
        self.brfa = brfa

    def run(self):
        for page in self.category:
            if page.title() == "Template:Uw-corpname":
                continue
            # print(page.title())
            if page.title()[:10] != "User talk:":
                print("NOT RIGHT FORMAT " + page.title())
                continue
            user = self.generate_user(page)
            if not user.isBlocked():
                self.log(page)
                old_t = page.text
                self.category_remove(self.target, page)
                if page.text == old_t:
                    print("Move to backup")
                    self.category_remove(self.backup_target, page)
                page.save(
                    summary="Removing [[Category:" + self.cat_name + "]] as user is unblocked." +
                            " ([[Wikipedia:Bots/Requests for approval/" + self.brfa + "|BRFA]])", minor=True,
                    botflag=True, force=True)
                print("Saved " + str(page.title()))
