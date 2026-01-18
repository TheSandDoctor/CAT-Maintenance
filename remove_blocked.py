from RemoveBase import RemoveBlocked
from datetime import date

if __name__ == "__main__":
    today = date.today()
    rmBlocked = RemoveBlocked(
        log_name="block_removed_" + today.strftime("%b_%d_%Y") + ".txt",
        category="Wikipedia usernames with possible policy issues",  # Parent category
        target=None,  # Will be auto-generated per subcategory
        brfa="TheSandBot 6",
        process_subcategories=True
    )

    try:
        rmBlocked.run()
    except KeyboardInterrupt:
        print("\n")
    # # months = ['January 2025', 'February 2025', 'March 2025', 'April 2025', 'May 2025', 'June 2025', 'July 2025', "August 2025", "September 2025", "October 2025"]#, "November 2024", "December 2024"]
    # months = ['December 2025']
    # for month in months:
    #     print(f"Running {month}")
    #     rmBlocked = RemoveBlocked(
    #         log_name="block_removed_" + today.strftime("%b_%d_%Y") + ".txt",
    #         category=f"Wikipedia usernames with possible policy issues from {month}",
    #         target=f"[[Category:Wikipedia usernames with possible policy issues from {month}|{{{{PAGENAME}}}}]]",
    #         brfa="TheSandBot 6"
    #     )
