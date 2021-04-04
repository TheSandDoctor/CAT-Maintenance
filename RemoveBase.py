import pywikibot
import re
import requests
#import datetime
from datetime import *
from dateutil import relativedelta

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
    def __init__(self, log_name, category, target, brfa, span=None, trial=False, count=50):
        super(RemoveBlocked, self).__init__(log_name, category, trial)
        self.target = target
        self.brfa = brfa
        self.span = span
        if trial:
            self.count = count

    def run(self):
        counter = 0
        for page in self.category:
            if page.title() == "Template:Uw-corpname":
                continue
            if self.trial:
                if counter >= self.count:
                    print("\n\nDONE TRIAL\n\n")
                    return
            try:
                user = self.generate_user(page)
            except AttributeError:
                print("Failed" + page.title())
                continue
            summary = "Removing [[Category:" + self.cat_name + "]] as "
            #print(user.username)
            try:
                if self.isLocked(user.username):
                    self.log(page)
                    self.category_remove(self.target, page)
                    page.save(
                        summary=summary + "user is locked." +
                                " ([[Wikipedia:Bots/Requests for approval/" + self.brfa + "|BRFA]])", minor=True,
                        botflag=True, force=True)
                    #print("Saved " + str(page.title()))
                    if self.trial:
                        counter += 1
                        print(counter)
                elif user.isBlocked():
                    self.log(page)
                    self.category_remove(self.target, page)
                    page.save(
                        summary=summary + "user is blocked." +
                                " ([[Wikipedia:Bots/Requests for approval/" + self.brfa + "|BRFA]])", minor=True,
                        botflag=True, force=True)
                    #print("Saved " + str(page.title()))
                    if self.trial:
                        counter += 1
                        print(counter)
            except KeyError:
                #print("No global account")
                if user.isBlocked():
                    self.log(page)
                    self.category_remove(self.target, page)
                    page.save(
                        summary=summary + "user is blocked." +
                                " ([[Wikipedia:Bots/Requests for approval/" + self.brfa + "|BRFA]])", minor=True,
                        botflag=True, force=True)
                    #print("Saved " + str(page.title()))
                    if self.trial:
                        counter += 1
                        print(counter)
            if self.span is not None and type(self.span) != int:
                #print(user.isAnonymous())
                span1 = datetime.strptime(self.span, "%Y-%m-%dT%H:%M:%SZ")
                if user.isAnonymous():
                    page_date = datetime.strptime(str(page.latest_revision.timestamp), "%Y-%m-%dT%H:%M:%SZ")
                    #print(span1 > dt)
                    #print(self.calc_difference(page.latest_revision.timestamp))
                    #sample = {'year':2018,'month':02,'day':01}
                    #b2 = date(sample[0], sample[1], d2)
                    if page_date <= span1:#int(str(page.latest_revision.timestamp)[0:4]) <= self.span:
                        self.log(page)
                        self.category_remove(self.target, page)
                        page.save(
                            summary=summary + "talk page not edited in " +
                                    self.calc_difference(page.latest_revision.timestamp) +
                                    " and notice considered stale." + " ([[Wikipedia:Bots/Requests for approval/" +
                                    self.brfa + "|BRFA]])", minor=True,
                            botflag=True, force=True)
                else:
                    #print(user.username)
                    results = []
                    if user.last_event is not None:
                        event_timestamp = user.last_event.timestamp()
                        ev_ts = datetime.strptime(str(event_timestamp), "%Y-%m-%dT%H:%M:%SZ")
                        results.append(ev_ts)

                    if user.last_edit is not None:
                        user_edit = user.last_edit[2]
                        ed_ts = datetime.strptime(str(user_edit), "%Y-%m-%dT%H:%M:%SZ")
                        results.append(ed_ts)

                    try:
                        dcontribs = next(iter(user.deleted_contributions()))
                        del_ts = datetime.strptime(str(dcontribs[1]['timestamp']), "%Y-%m-%dT%H:%M:%SZ")
                        results.append(del_ts)
                    except StopIteration:
                        pass # No deleted contribs

                    #Compare last event edit, last edit,
                    #last deleted edit to figure the most recent
                    newest_contrib_time = max(results)
                    #print(newest_contrib_time)

                    if newest_contrib_time <= span1:
                        self.log(page)
                        self.category_remove(self.target, page)
                        page.save(
                            summary=summary + "user has not edited in " +
                                    self.calc_difference(newest_contrib_time) +
                                    " and notice considered stale."+ " ([[Wikipedia:Bots/Requests for approval/" +
                                    self.brfa + "|BRFA]])", minor=True,
                                    botflag=True, force=True
                        )


    def calc_difference(self, old_date):
        now = datetime.utcnow()
        diff = relativedelta.relativedelta(now, old_date)
        result = ""
        if diff.years > 1:
            result += "%s years, " % diff.years
        elif diff.years == 1:
            result += "%s year, and " % diff.years
        if diff.months > 1:
            result += "%s months, " % diff.months
        elif diff.months == 1:
            result += "%s month, and " % diff.months
        if diff.days > 1:
            result += "%s days, " % diff.days
        elif diff.days == 1:
            result += "%s day, and " % diff.days
        if diff.hours > 1:
            result += "%s hours " % diff.hours
        elif diff.hours == 1:
            result += "%s hour " % diff.hours

        return result  # %(diff.years, diff.months, diff.days, diff.hours)


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
                #print("Saved " + str(page.title()))
