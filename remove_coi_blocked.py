from RemoveBase import RemoveBlocked
from datetime import date
from requests import ConnectionError

if __name__ == "__main__":
    today = date.today()
    rmBlocked = RemoveBlocked(log_name="block_coi_removed_" + \
                                    today.strftime("%b_%d_%Y") + ".txt",
                              category="User talk pages with conflict of interest notices",
                              target="[[Category:User talk pages with conflict of interest notices|{{PAGENAME}}]]",
                              brfa="TheSandBot 10",
span="2024-12-30T00:00:00Z")

    num_failures = 0
    while True:
        try:
            rmBlocked.run()
            break
        except KeyboardInterrupt:
            print("\n")
            break
        except ConnectionError:
            if num_failures > 30:
                raise Exception("Unable to complete, ConnectionError")
            else:
                num_failures += 1
