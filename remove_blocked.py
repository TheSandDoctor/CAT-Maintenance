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