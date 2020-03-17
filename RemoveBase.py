import pywikibot
import re


class RemoveBase:
    def __init__(self, log_name, category):
        self.pattern = r'(?:User talk:)([^/\n]+)'
        self.site = pywikibot.Site(fam="wikipedia", code="en", user="TheSandBot")
        self.count = 0
        self.log_filename = log_name
        self.category = pywikibot.Category(self.site, category).articles()
        self.cat_name = category

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

    def run(self):
        pass

    def log(self, page):
        with open(self.log_filename, 'a+') as f:
            self.count += 1
            f.write(str(self.count) + " " + str(page.title()) + "\n")


class RemoveBlocked(RemoveBase):
    def __init__(self, log_name, category, target, brfa):
        super(RemoveBlocked, self).__init__(log_name, category)
        self.target = target
        self.brfa = brfa

    def run(self):
        for page in self.category:
            if page.title() == "Template:Uw-corpname":
                continue
            user = self.generate_user(page)
            if user.isBlocked():
                self.log(page)
                self.category_remove(self.target, page)
                page.save(
                    summary="Removing " + self.cat_name + " as user is blocked." +
                            " ([[" + self.brfa + "|BRFA]])", minor=True,
                    botflag=True, force=True)
                print("Saved " + str(page.title()))


class RemoveUnblocked(RemoveBase):
    def __init__(self, log_name, category, target, brfa):
        super(RemoveUnblocked, self).__init__(log_name, category)
        self.target = target
        self.brfa = brfa

    def run(self):
        for page in self.category:
            if page.title() == "Template:Uw-corpname":
                continue
            user = self.generate_user(page)
            if not user.isBlocked():
                self.log(page)
                self.category_remove(self.target, page)
                page.save(
                    summary="Removing " + self.cat_name + " as user is unblocked." +
                            " ([[Wikipedia:Bots/Requests for approval/" + self.brfa + "|BRFA]])", minor=True,
                    botflag=True, force=True)
                print("Saved " + str(page.title()))