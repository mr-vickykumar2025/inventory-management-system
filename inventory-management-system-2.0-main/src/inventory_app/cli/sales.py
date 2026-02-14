from .. import database
from datetime import datetime


def _read_positive_float(prompt):
    try:
        value = float(input(prompt))
    except ValueError:
        print("Invalid input format.")
        return None
    if value <= 0:
        print("Quantity must be greater than zero.")
        return None
    return value


# ---------------- SALES DASHBOARD ----------------

def sales_dashboard():
    while True:
        print("\n========== SALES MODULE ==========")
        print("1. Sell Product")
        print("2. View Products")
        print("3. Back to Main Menu")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            sell_product()
        elif choice == "2":
            view_products()
        elif choice == "3":
            break
        else:
            print("\nInvalid choice. Try again.\n")


# ---------------- SELL PRODUCT ----------------

def sell_product():
    print("\n--- Sell Product ---")

    product_id = input("Enter Product ID: ").strip()
    if not product_id:
        print("Product ID is required.")
        return

    quantity = _read_positive_float("Enter Quantity: ")
    if quantity is None:
        return

    product = database.get_product_by_id(product_id)

    if not product:
        print("Product not found.")
        return

    product_name = product[1]
    unit = product[3] or "unit"
    price = product[4]
    stock = product[5]

    if quantity > stock:
        print(f"Insufficient stock. Available: {stock}")
        return

    total = price * quantity

    print("\n========== BILL ==========")
    print(f"Product   : {product_name}")
    print(f"Price     : {price} per {unit}")
    if product[3]:
        print(f"Quantity  : {quantity} {product[3]}")
    else:
        print(f"Quantity  : {quantity}")
    print(f"Total     : {total}")
    print(f"Date      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==========================")

    confirm = input("\nConfirm sale? (y/n): ").lower()

    if confirm == "y":
        result = database.record_sale(product_id, quantity)
        print(f"\n{result}\n")
    else:
        print("\nSale cancelled.\n")


# ---------------- VIEW PRODUCTS ----------------

def view_products():
    print("\n========== PRODUCT LIST ==========")
    query = input("Search (leave blank for all): ").strip()
    products = database.search_products(query) if query else database.get_all_products()

    if not products:
        print("No products available.")
        return

    print("\nID | Name | Category | Unit | Price | Stock")
    print("-----------------------------------------------")

    for p in products:
        print(f"{p[0]} | {p[1]} | {p[2]} | {p[3]} | {p[4]} | {p[5]}")
