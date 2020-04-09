from RemoveBase import RemoveUnblocked

if __name__ == "__main__":
    rmBlocked = RemoveUnblocked(log_name="unblocked_removed_mar_17_2020.txt",
                                category="Wikipedians who are indefinitely blocked for promotional user names",
                                target="[[Category:Wikipedians who are indefinitely blocked for promotional user names|{{PAGENAME}}]]",
                                backup_target="[[Category:Wikipedians who are indefinitely blocked for promotional user names||{{PAGENAME}}]]",
                                brfa="TheSandBot 7")
    try:
        rmBlocked.run()
    except KeyboardInterrupt:
        print("\n")
