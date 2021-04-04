from RemoveBase import RemoveBlocked
from datetime import date

if __name__ == "__main__":
    today = date.today()
    rmBlocked = RemoveBlocked(log_name="block_coi_removed_" + \
                                    today.strftime("%b_%d_%Y") + ".txt",
                              category="User talk pages with conflict of interest notices",
                              target="[[Category:User talk pages with conflict of interest notices|{{PAGENAME}}]]",
                              brfa="TheSandBot 10", span="2019-02-02T00:00:00Z")
    try:
        rmBlocked.run()
    except KeyboardInterrupt:
        print("\n")
