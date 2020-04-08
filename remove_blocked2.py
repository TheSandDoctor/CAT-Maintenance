from RemoveBase import RemoveBlocked

if __name__ == "__main__":
    rmBlocked = RemoveBlocked(log_name="block_removed_apr_3_2020.txt",
                              category="Wikipedia usernames with possible policy issues",
                              target="[[Category:Wikipedia usernames with possible policy issues|{{PAGENAME}}]]",
                              brfa="TheSandBot 6")
    try:
        rmBlocked.run()
    except KeyboardInterrupt:
        print("\n")
