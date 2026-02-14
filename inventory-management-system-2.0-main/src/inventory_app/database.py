# -*- coding: utf-8 -*-
import sqlite3
import hashlib
import os
import sys
import hmac
from datetime import datetime

def _resolve_app_base():
    override = os.getenv("INVENTORY_APP_HOME")
    if override:
        return override
    if getattr(sys, "frozen", False):
        base = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, "InventoryApp")
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

BASE_DIR = _resolve_app_base()
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_NAME = os.path.join(DATA_DIR, "inventory.db")
LOW_STOCK_LIMIT = 10

def get_app_base_dir():
    return BASE_DIR

def has_any_user():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users LIMIT 1")
    row = cursor.fetchone()
    if row:
        conn.close()
        return True
    cursor.execute("SELECT 1 FROM admin LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row is not None

# FIX: timeout + thread safe
def connect_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    return sqlite3.connect(DB_NAME, timeout=10, check_same_thread=False)

def _ensure_sales_columns(cursor):
    cursor.execute("PRAGMA table_info(sales)")
    cols = {row[1] for row in cursor.fetchall()}
    if "product_name" not in cols:
        cursor.execute("ALTER TABLE sales ADD COLUMN product_name TEXT")
    if "unit_price" not in cols:
        cursor.execute("ALTER TABLE sales ADD COLUMN unit_price REAL")

def _sales_has_snapshot_columns(cursor):
    cursor.execute("PRAGMA table_info(sales)")
    cols = {row[1] for row in cursor.fetchall()}
    return "product_name" in cols and "unit_price" in cols

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT,
        unit TEXT,
        price REAL,
        quantity REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id TEXT,
        product_name TEXT,
        unit_price REAL,
        quantity_sold REAL,
        total_price REAL,
        sale_date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        action TEXT,
        details TEXT,
        created_at TEXT
    )
    """)

    _ensure_sales_columns(cursor)

    conn.commit()
    conn.close()

# ---------- ADMIN ----------

# ---------- USERS / AUTH ----------

def _hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)
    pwd = password.encode("utf-8")
    key = hashlib.pbkdf2_hmac("sha256", pwd, salt, 100000)
    return salt.hex(), key.hex()

def _verify_password(password, salt_hex, hash_hex):
    salt = bytes.fromhex(salt_hex)
    pwd = password.encode("utf-8")
    key = hashlib.pbkdf2_hmac("sha256", pwd, salt, 100000)
    return hmac.compare_digest(key.hex(), hash_hex)

def create_user(username, password, role):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return False
    role = role.lower()
    salt_hex, hash_hex = _hash_password(password)
    cursor.execute(
        "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
        (username, hash_hex, salt_hex, role)
    )
    conn.commit()
    conn.close()
    return True

def validate_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, salt, role FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("SELECT 1 FROM admin WHERE username=? AND password=?", (username, password))
        legacy = cursor.fetchone()
        conn.close()
        if legacy:
            create_user(username, password, "admin")
            return "admin"
        return None
    password_hash, salt, role = row
    conn.close()
    if not _verify_password(password, salt, password_hash):
        return None
    return role

def create_admin(username, password):
    return create_user(username, password, "admin")

def validate_admin(username, password):
    role = validate_user(username, password)
    if role == "admin":
        return True
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM admin WHERE username=? AND password=?", (username, password))
    data = cursor.fetchone()
    conn.close()
    return data is not None

# ---------- PRODUCTS ----------

def add_product(pid, name, category, unit, price, quantity):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)",
                   (pid, name, category, unit, price, quantity))
    conn.commit()
    conn.close()

def update_product(pid, name, category, unit, price, quantity):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET product_name=?, category=?, unit=?, price=?, quantity=? WHERE product_id=?",
        (name, category, unit, price, quantity, pid)
    )
    conn.commit()
    conn.close()

def get_all_products():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()
    conn.close()
    return data

def _normalize_query(query):
    if query is None:
        return ""
    return str(query).strip()

def search_products(query):
    query = _normalize_query(query)
    if not query:
        return get_all_products()

    like = f"%{query}%"
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM products
        WHERE product_id LIKE ?
           OR product_name LIKE ?
           OR category LIKE ?
           OR unit LIKE ?
    """, (like, like, like, like))
    data = cursor.fetchall()
    conn.close()
    return data

def get_product_by_id(pid):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id=?", (pid,))
    data = cursor.fetchone()
    conn.close()
    return data

def delete_product(pid):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE product_id=?", (pid,))
    conn.commit()
    conn.close()

def get_low_stock_products():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE quantity <= ?", (LOW_STOCK_LIMIT,))
    data = cursor.fetchall()
    conn.close()
    return data

# ---------- SALES ----------

def record_sale(pid, qty):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT product_name, price, quantity FROM products WHERE product_id=?", (pid,))
    product = cursor.fetchone()

    if not product:
        conn.close()
        return "Product not found"

    name, price, stock = product

    if qty > stock:
        conn.close()
        return "Insufficient stock"

    total = price * qty
    date = datetime.now().strftime("%d-%m-%Y %H:%M")

    cursor.execute("""
        INSERT INTO sales (product_id, product_name, unit_price, quantity_sold, total_price, sale_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (pid, name, price, qty, total, date))

    cursor.execute("UPDATE products SET quantity=? WHERE product_id=?", (stock - qty, pid))

    conn.commit()
    conn.close()
    return "Sale successful"

def get_sales_history():
    conn = connect_db()
    cursor = conn.cursor()

    if _sales_has_snapshot_columns(cursor):
        cursor.execute("""
            SELECT sales.sale_id,
                   sales.product_id,
                   COALESCE(sales.product_name, products.product_name),
                   COALESCE(sales.unit_price, products.price),
                   sales.quantity_sold,
                   sales.total_price,
                   sales.sale_date
            FROM sales
            LEFT JOIN products ON sales.product_id = products.product_id
            ORDER BY sales.sale_id DESC
        """)
    else:
        cursor.execute("""
            SELECT sales.sale_id,
                   sales.product_id,
                   products.product_name,
                   products.price,
                   sales.quantity_sold,
                   sales.total_price,
                   sales.sale_date
            FROM sales
            JOIN products ON sales.product_id = products.product_id
            ORDER BY sales.sale_id DESC
        """)

    data = cursor.fetchall()
    conn.close()
    return data

def search_sales_history(query):
    query = _normalize_query(query)
    if not query:
        return get_sales_history()

    like = f"%{query}%"
    conn = connect_db()
    cursor = conn.cursor()

    if _sales_has_snapshot_columns(cursor):
        cursor.execute("""
            SELECT sales.sale_id,
                   sales.product_id,
                   COALESCE(sales.product_name, products.product_name),
                   COALESCE(sales.unit_price, products.price),
                   sales.quantity_sold,
                   sales.total_price,
                   sales.sale_date
            FROM sales
            LEFT JOIN products ON sales.product_id = products.product_id
            WHERE sales.product_id LIKE ?
               OR COALESCE(sales.product_name, products.product_name) LIKE ?
               OR sales.sale_date LIKE ?
            ORDER BY sales.sale_id DESC
        """, (like, like, like))
    else:
        cursor.execute("""
            SELECT sales.sale_id,
                   sales.product_id,
                   products.product_name,
                   products.price,
                   sales.quantity_sold,
                   sales.total_price,
                   sales.sale_date
            FROM sales
            JOIN products ON sales.product_id = products.product_id
            WHERE sales.product_id LIKE ?
               OR products.product_name LIKE ?
               OR sales.sale_date LIKE ?
            ORDER BY sales.sale_id DESC
        """, (like, like, like))

    data = cursor.fetchall()
    conn.close()
    return data

# ---------- AUDIT LOG ----------

def log_action(username, action, details=""):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_logs (username, action, details, created_at) VALUES (?, ?, ?, ?)",
        (username, action, details, datetime.now().strftime("%d-%m-%Y %H:%M"))
    )
    conn.commit()
    conn.close()

def get_audit_logs(limit=200):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT log_id, username, action, details, created_at
        FROM audit_logs
        ORDER BY log_id DESC
        LIMIT ?
    """, (limit,))
    data = cursor.fetchall()
    conn.close()
    return data

def search_audit_logs(query, limit=200):
    query = _normalize_query(query)
    if not query:
        return get_audit_logs(limit=limit)

    like = f"%{query}%"
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT log_id, username, action, details, created_at
        FROM audit_logs
        WHERE username LIKE ?
           OR action LIKE ?
           OR details LIKE ?
           OR created_at LIKE ?
        ORDER BY log_id DESC
        LIMIT ?
    """, (like, like, like, like, limit))
    data = cursor.fetchall()
    conn.close()
    return data

# ---------- BACKUP / RESTORE ----------

def backup_database(target_path):
    source = connect_db()
    dest = sqlite3.connect(target_path)
    with dest:
        source.backup(dest)
    dest.close()
    source.close()

def restore_database(source_path):
    source = sqlite3.connect(source_path)
    dest = connect_db()
    with dest:
        source.backup(dest)
    dest.close()
    source.close()
    create_tables()

