from RemoveBase import RemoveUnblocked
from datetime import date

if __name__ == "__main__":
    today = date.today()
    rmBlocked = RemoveUnblocked(log_name="unblocked_removed_" + \
                                    today.strftime("%b_%d_%Y") + ".txt",
                                category="Wikipedians who are indefinitely blocked for promotional user names",
                                target="[[Category:Wikipedians who are indefinitely blocked for promotional user names|{{PAGENAME}}]]",
                                backup_target="[[Category:Wikipedians who are indefinitely blocked for promotional user names||{{PAGENAME}}]]",
                                brfa="TheSandBot 7")
    try:
        rmBlocked.run()
    except KeyboardInterrupt:
        print("\n")
