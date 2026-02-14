from .. import database


def _read_text(prompt):
    return input(prompt).strip()


def _read_positive_float(prompt):
    try:
        value = float(input(prompt))
    except ValueError:
        print("Invalid number.")
        return None
    if value <= 0:
        print("Value must be greater than zero.")
        return None
    return value


# ---------------- ADMIN LOGIN ----------------

def admin_login():
    print("\n===== ADMIN LOGIN =====")
    username = input("Username: ")
    password = input("Password: ")

    if database.validate_admin(username, password):
        print("\nLogin successful.\n")
        admin_dashboard()
    else:
        print("\nInvalid credentials. Access denied.\n")


# ---------------- ADMIN DASHBOARD ----------------

def admin_dashboard():
    while True:
        print("\n========== ADMIN DASHBOARD ==========")
        print("1. Add Product")
        print("2. Update Stock")
        print("3. Delete Product")
        print("4. View Inventory")
        print("5. View Sales Report")
        print("6. View Low Stock Products")
        print("7. Logout")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            add_product()
        elif choice == "2":
            update_stock()
        elif choice == "3":
            delete_product()
        elif choice == "4":
            view_inventory()
        elif choice == "5":
            view_sales_report()
        elif choice == "6":
            view_low_stock()
        elif choice == "7":
            print("\nLogging out...\n")
            break
        else:
            print("\nInvalid choice. Please try again.\n")


# ---------------- PRODUCT MANAGEMENT ----------------

def add_product():
    print("\n--- Add New Product ---")
    product_id = _read_text("Product ID: ")
    name = _read_text("Product Name: ")
    if not product_id or not name:
        print("Product ID and Name are required.")
        return
    category = _read_text("Category (optional): ") or None
    unit = _read_text("Unit (optional): ") or None

    price = _read_positive_float("Price: ")
    quantity = _read_positive_float("Quantity: ")
    if price is None or quantity is None:
        return

    if database.get_product_by_id(product_id):
        print("Product ID already exists.")
        return

    try:
        database.add_product(product_id, name, category, unit, price, quantity)
        print("\nProduct added successfully.\n")
    except Exception as exc:
        print(f"\nFailed to add product: {exc}\n")


def update_stock():
    print("\n--- Update Stock ---")

    product_id = _read_text("Product ID: ")
    if not product_id:
        print("Product ID is required.")
        return

    new_quantity = _read_positive_float("New Quantity: ")
    if new_quantity is None:
        return

    product = database.get_product_by_id(product_id)

    if not product:
        print("Product not found.")
        return

    database.update_product(
        product_id,
        product[1],
        product[2],
        product[3],
        product[4],
        new_quantity
    )
    print("\nStock updated successfully.\n")


def delete_product():
    print("\n--- Delete Product ---")

    product_id = _read_text("Product ID: ")
    if not product_id:
        print("Product ID is required.")
        return

    product = database.get_product_by_id(product_id)

    if not product:
        print("Product not found.")
        return

    database.delete_product(product_id)
    print("\nProduct deleted successfully.\n")


# ---------------- VIEW FUNCTIONS ----------------

def view_inventory():
    print("\n========== INVENTORY ==========")
    query = input("Search (leave blank for all): ").strip()
    products = database.search_products(query) if query else database.get_all_products()

    if not products:
        print("No products found.")
        return

    print("\nID | Name | Category | Unit | Price | Quantity")
    print("-----------------------------------------------")

    for p in products:
        print(f"{p[0]} | {p[1]} | {p[2]} | {p[3]} | {p[4]} | {p[5]}")


def view_sales_report():
    print("\n========== SALES REPORT ==========")
    query = input("Search (leave blank for all): ").strip()
    report = database.search_sales_history(query) if query else database.get_sales_history()

    if not report:
        print("No sales records found.")
        return

    print("\nSaleID | Product ID | Product | Price | Qty | Total | Date")
    print("------------------------------------------------------------")

    for r in report:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]}")


def view_low_stock():
    print("\n========== LOW STOCK PRODUCTS ==========")
    query = input("Search (leave blank for all): ").strip()
    if query:
        limit = getattr(database, "LOW_STOCK_LIMIT", 10)
        products = [p for p in database.search_products(query) if p[5] <= limit]
    else:
        products = database.get_low_stock_products()

    if not products:
        print("No low-stock products.")
        return

    print("\nID | Name | Category | Unit | Price | Quantity")
    print("-----------------------------------------------")

    for p in products:
        print(f"{p[0]} | {p[1]} | {p[2]} | {p[3]} | {p[4]} | {p[5]}")
