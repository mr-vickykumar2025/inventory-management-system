from .. import database
from . import admin
from . import sales


def _ensure_first_admin():
    if database.has_any_user():
        return
    print("\n=== First-Time Setup ===")
    while True:
        password = input("Set admin password (min 6 chars): ").strip()
        confirm = input("Confirm password: ").strip()
        if not password:
            print("Password is required.")
            continue
        if len(password) < 6:
            print("Password must be at least 6 characters.")
            continue
        if password != confirm:
            print("Passwords do not match.")
            continue
        database.create_user("admin", password, "admin")
        print("Admin created. Please login.")
        break


def main_menu():
    while True:
        print("\n========== INVENTORY MANAGEMENT SYSTEM ==========")
        print("1. Admin Login")
        print("2. Sales Module")
        print("3. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            admin.admin_login()
        elif choice == "2":
            sales.sales_dashboard()
        elif choice == "3":
            print("\nExiting system... Goodbye.\n")
            break
        else:
            print("\nInvalid choice. Please try again.\n")


if __name__ == "__main__":
    # Initialize database and tables
    database.create_tables()
    _ensure_first_admin()

    print("\nSystem initialized successfully.")
    main_menu()

def run():
    database.create_tables()
    _ensure_first_admin()
    print("\nSystem initialized successfully.")
    main_menu()
