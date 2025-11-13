
import sqlite3
import os
import json

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db(db_path='grocery.db'):
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    return conn

def init_db(db_path='grocery.db'):
    if os.path.exists(db_path):
        return
    db = sqlite3.connect(db_path)
    cur = db.cursor()
    cur.execute('''CREATE TABLE products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL, stock INTEGER)''')
    cur.execute('''CREATE TABLE sales (id INTEGER PRIMARY KEY AUTOINCREMENT, items_json TEXT, total REAL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    cur.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'customer', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    sample = [
        ('Rice 5kg', 350.0, 20),
        ('Wheat 5kg', 300.0, 15),
        ('Sugar 1kg', 45.0, 50),
        ('Milk 1L', 35.0, 100)
    ]
    cur.executemany('INSERT INTO products (name, price, stock) VALUES (?, ?, ?)', sample)

    # Create default admin user (email: admin@quickbasket.com, password: admin123)
    import hashlib
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    cur.execute('INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)',
                ('admin@quickbasket.com', admin_password, 'admin'))

    # Create default customer user (email: customer@quickbasket.com, password: customer123)
    customer_password = hashlib.sha256('customer123'.encode()).hexdigest()
    cur.execute('INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)',
                ('customer@quickbasket.com', customer_password, 'customer'))

    db.commit()
    db.close()
