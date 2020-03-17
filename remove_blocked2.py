from RemoveBase import RemoveBlocked

if __name__ == "__main__":
    rmBlocked = RemoveBlocked(log_name="block_removed_mar_14_2020.txt",
                              category="[[:Category:Wikipedia usernames with possible policy issues]]",
                              target="[[Category:Wikipedia usernames with possible policy issues|{{PAGENAME}}]]",
                              brfa="TheSandBot 6")
    rmBlocked.run()