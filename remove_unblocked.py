from RemoveBase import RemoveUnblocked

if __name__ == "__main__":
    rmBlocked = RemoveUnblocked(log_name="unblocked_removed_mar_17_2020.txt",
                              category="[[:Category:Wikipedians who are indefinitely blocked for promotional user names]]",
                              target="[[Category:Wikipedians who are indefinitely blocked for promotional user names|{{PAGENAME}}]]",
                              brfa="TheSandBot 7")
    rmBlocked.run()