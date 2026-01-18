import pywikibot
import re
from datetime import *
import datetime as dt
from dateutil import relativedelta
from pywikibot.exceptions import InvalidTitleError, APIMWError

class RemoveBase:
    def __init__(self, log_name, category, trial = False, process_subcategories = False):
        self.pattern = r'(?:User talk:)([^/\n]+)'
        self.site = pywikibot.Site()  # fam="wikipedia", code="en", user="TheSandBot")
        self.site.login()
        self.count = 0
        self.log_filename = log_name
        self.process_subcategories = process_subcategories
        try:
            if process_subcategories:
                self.parent_category_obj = pywikibot.Category(self.site, category)
                self.parent_category_name = category
                self.category = None  # Will be set per subcategory in run()
            else:
                self.category = pywikibot.Category(self.site, category).articles()
        except InvalidTitleError:
            print("\nBad category title")
            exit()
        self.cat_name = category
        self.trial = trial

    def category_remove(self, target: str, page: pywikibot.Page) -> None:
        """
        Helper method to remove target from page text.

        :param target: Target category to remove
        :param page: The page object to edit
        :return: None
        """
        page.text = page.text.replace(target, "")

    def generate_user(self, page: pywikibot.Page) -> pywikibot.User:
        m = re.search(self.pattern, str(page.title()))
        user_raw = m.group(1)
        return pywikibot.User(self.site, user_raw)

    def log(self, page):
        with open(self.log_filename, 'a+') as f:
            f.write(str(page.title()) + "\n")


class RemoveBlocked(RemoveBase):
    def __init__(self, log_name, category, target, brfa, span=None, trial=False, count=50, process_subcategories=False):
        """

        :param log_name: Filename for log of pages removed.
        :param category: Category to process.
        :param target: Target category to remove
        :param brfa: BRFA subpage that provides approval
        :param span: Example: "2025-06-30T00:00:00Z", True for 12 months ago, None for no span
        :param trial: Whether to run in trial mode.
        :param count: Number of pages to process in trial mode.
        :param process_subcategories: Whether to process all subcategories of the parent category
        """
        super(RemoveBlocked, self).__init__(log_name, category, trial, process_subcategories=process_subcategories)
        self.target = target
        self.brfa = brfa
        # Handle span: if True, calculate 12 months ago from UTC; if string, use as-is; if None, keep None
        if isinstance(span, bool) and span:
            six_months_ago = datetime.now(dt.UTC) - relativedelta.relativedelta(years=1)
            self.span = six_months_ago.strftime("%Y-%m-%dT%H:%M:%SZ")
            print(f"Running for span: {self.span}")
        else:
            self.span = span
        if trial:
            self.count = count

    def _process_page(self, page, target, cat_name, counter):
        """Helper method to process a single page with given target and category name."""
        if page.title() == "Template:Uw-corpname":
            return counter
        if self.trial:
            if counter >= self.count:
                print("\n\nDONE TRIAL\n\n")
                return counter
        try:
            user = self.generate_user(page)
        except AttributeError:
            print("Failed " + page.title())
            return counter
        summary = "Removing [[Category:" + cat_name + "]] as "
        try:
            if not user.isAnonymous() and user.is_locked():
                self.log(page)
                self.category_remove(target, page)
                page.save(
                    summary=summary + "user is locked." +
                            " ([[Wikipedia:Bots/Requests for approval/" + self.brfa + "|BRFA]])", minor=True,
                    botflag=True, force=True)
                if self.trial:
                    counter += 1
                    print(counter)
                return counter
            elif user.is_blocked():
                self.log(page)
                self.category_remove(target, page)
                page.save(
                    summary=summary + "user is blocked." +
                            " ([[Wikipedia:Bots/Requests for approval/" + self.brfa + "|BRFA]])", minor=True,
                    botflag=True, force=True)
                if self.trial:
                    counter += 1
                    print(counter)
                return counter
        except KeyError:
            if user.is_blocked():
                self.log(page)
                self.category_remove(target, page)
                page.save(
                    summary=summary + "user is blocked." +
                            " ([[Wikipedia:Bots/Requests for approval/" + self.brfa + "|BRFA]])", minor=True,
                    botflag=True, force=True)
                if self.trial:
                    counter += 1
                    print(counter)
                return counter
        if self.span is not None and type(self.span) != int:
            span1 = datetime.strptime(self.span, "%Y-%m-%dT%H:%M:%SZ")
            if user.isAnonymous():
                page_date = datetime.strptime(str(page.latest_revision.timestamp), "%Y-%m-%dT%H:%M:%SZ")
                if page_date <= span1:
                    self.log(page)
                    self.category_remove(target, page)
                    page.save(
                        summary=summary + "talk page not edited in " +
                                self.calc_difference(page.latest_revision.timestamp) +
                                " and notice considered stale." + " ([[Wikipedia:Bots/Requests for approval/" +
                                self.brfa + "|BRFA]])", minor=True,
                        botflag=True, force=True)
                return counter
            else:
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
                except APIMWError:
                    print("Failed to get deleted contributions for " + page.title())

                if not results:
                    page_date = datetime.strptime(str(page.latest_revision.timestamp), "%Y-%m-%dT%H:%M:%SZ")
                    if page_date <= span1:
                        self.log(page)
                        self.category_remove(target, page)
                        page.save(
                            summary=summary + "talk page not edited in " +
                                    self.calc_difference(page.latest_revision.timestamp) +
                                    " and notice considered stale." + " ([[Wikipedia:Bots/Requests for approval/" +
                                    self.brfa + "|BRFA]])", minor=True,
                            botflag=True, force=True)
                        return counter
                    return counter # Page edit more recent than our cutoff, so do nothing and return

                # Compare last event edit, last edit, last deleted edit to figure the most recent
                try:
                    newest_contrib_time = max(results)
                except ValueError:
                    print(page)
                    raise
                if newest_contrib_time <= span1:
                    self.log(page)
                    self.category_remove(target, page)
                    page.save(
                        summary=summary + "user has not edited in " +
                                self.calc_difference(newest_contrib_time) +
                                " and notice considered stale."+ " ([[Wikipedia:Bots/Requests for approval/" +
                                self.brfa + "|BRFA]])", minor=True,
                                botflag=True, force=True
                    )
        return counter

    def run(self):
        counter = 0
        if self.process_subcategories:
            # Process all subcategories of the parent category
            for subcat in self.parent_category_obj.subcategories():  # type: pywikibot.Category
                subcat_title = subcat.title()
                # Extract name part (remove "Category:" prefix)
                if subcat_title.startswith("Category:"):
                    cat_name = subcat_title[len("Category:"):]
                else:
                    cat_name = subcat_title
                print("Working through subcategory: " + cat_name)
                # Build target dynamically
                target = f"[[Category:{cat_name}|{{{{PAGENAME}}}}]]"
                # Get articles from this subcategory
                for page in subcat.articles():
                    if self.trial and counter >= self.count:
                        print("\n\nDONE TRIAL\n\n")
                        return
                    counter = self._process_page(page, target, cat_name, counter)
                    if self.trial and counter >= self.count:
                        print("\n\nDONE TRIAL\n\n")
                        return
            return
        
        # Single-category mode
        for page in self.category:
            if self.trial and counter >= self.count:
                print("\n\nDONE TRIAL\n\n")
                return
            counter = self._process_page(page, self.target, self.cat_name, counter)
            if self.trial and counter >= self.count:
                print("\n\nDONE TRIAL\n\n")
                return


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

        return result


class RemoveUnblocked(RemoveBase):
    def __init__(self, log_name, category, target, backup_target, brfa, trial = False, process_subcategories=False):
        super(RemoveUnblocked, self).__init__(log_name, category, trial, process_subcategories=process_subcategories)
        self.target = target
        self.backup_target = backup_target
        self.brfa = brfa

    def run(self):
        if self.process_subcategories:
            # Process all subcategories of the parent category
            for subcat in self.parent_category_obj.subcategories():  # type: pywikibot.Category
                subcat_title = subcat.title()
                # Extract name part (remove "Category:" prefix)
                if subcat_title.startswith("Category:"):
                    cat_name = subcat_title[len("Category:"):]
                else:
                    cat_name = subcat_title
                # Build target dynamically
                target = f"[[Category:{cat_name}|{{{{PAGENAME}}}}]]"
                # Build backup_target dynamically (with double pipe)
                backup_target = f"[[Category:{cat_name}||{{{{PAGENAME}}}}]]"
                # Get articles from this subcategory
                for page in subcat.articles():
                    if page.title() == "Template:Uw-corpname":
                        continue
                    if page.title()[:10] != "User talk:":
                        print("NOT RIGHT FORMAT " + page.title())
                        continue
                    user = self.generate_user(page)
                    if not user.is_blocked():
                        self.log(page)
                        old_t = page.text
                        self.category_remove(target, page)
                        if page.text == old_t:
                            print("Move to backup")
                            self.category_remove(backup_target, page)
                        page.save(
                            summary="Removing [[Category:" + cat_name + "]] as user is unblocked." +
                                    " ([[Wikipedia:Bots/Requests for approval/" + self.brfa + "|BRFA]])", minor=True,
                            botflag=True, force=True)
            return
        
        # Single-category mode
        for page in self.category:
            if page.title() == "Template:Uw-corpname":
                continue
            if page.title()[:10] != "User talk:":
                print("NOT RIGHT FORMAT " + page.title())
                continue
            user = self.generate_user(page)
            if not user.is_blocked():
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
