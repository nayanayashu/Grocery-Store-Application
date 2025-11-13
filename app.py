
from flask import Flask, render_template, request, redirect, url_for, flash, g
import sqlite3, json
from db import init_db, get_db

app = Flask(__name__)
app.secret_key = 'replace-with-a-secure-key'

DATABASE = 'grocery.db'

@app.before_first_request
def setup():
    init_db(DATABASE)

@app.route('/')
def index():
    db = get_db(DATABASE)
    cur = db.execute('SELECT id, name, price, stock FROM products')
    products = cur.fetchall()
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    qty = int(request.form.get('quantity', 1))
    db = get_db(DATABASE)
    cur = db.execute('SELECT id, name, price, stock FROM products WHERE id=?', (product_id,))
    p = cur.fetchone()
    if not p:
        flash('Product not found.')
        return redirect(url_for('index'))
    if qty <= 0 or qty > p['stock']:
        flash('Invalid quantity or not enough stock.')
        return redirect(url_for('index'))
    cart = request.cookies.get('cart', '')
    pairs = {}
    if cart:
        for part in cart.split(','):
            if ':' in part:
                k,v = part.split(':')
                pairs[int(k)] = int(v)
    pairs[product_id] = pairs.get(product_id, 0) + qty
    new_cart = ','.join([f"{k}:{v}" for k,v in pairs.items()])
    resp = redirect(url_for('view_cart'))
    resp.set_cookie('cart', new_cart)
    flash(f'Added {qty} x {p["name"]} to cart.')
    return resp

@app.route('/cart')
def view_cart():
    cart = request.cookies.get('cart', '')
    items = []
    total = 0.0
    if cart:
        db = get_db(DATABASE)
        for part in cart.split(','):
            if ':' in part:
                pid, qty = part.split(':')
                cur = db.execute('SELECT id, name, price, stock FROM products WHERE id=?', (int(pid),))
                p = cur.fetchone()
                if p:
                    line = p['price'] * int(qty)
                    total += line
                    items.append({'id': p['id'], 'name': p['name'], 'price': p['price'], 'qty': int(qty), 'line': line})
    return render_template('cart.html', items=items, total=total)

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = request.cookies.get('cart', '')
    pairs = {}
    if cart:
        for part in cart.split(','):
            if ':' in part:
                k,v = part.split(':')
                pairs[int(k)] = int(v)
    if product_id in pairs:
        del pairs[product_id]
    new_cart = ','.join([f"{k}:{v}" for k,v in pairs.items()])
    resp = redirect(url_for('view_cart'))
    resp.set_cookie('cart', new_cart)
    flash('Item removed from cart.')
    return resp

@app.route('/checkout', methods=['POST'])
def checkout():
    cart = request.cookies.get('cart', '')
    if not cart:
        flash('Cart is empty.')
        return redirect(url_for('index'))
    db = get_db(DATABASE)
    pairs = {}
    for part in cart.split(','):
        if ':' in part:
            k,v = part.split(':')
            pairs[int(k)] = int(v)
    for pid, qty in pairs.items():
        cur = db.execute('SELECT stock FROM products WHERE id=?', (pid,))
        r = cur.fetchone()
        if not r or r['stock'] < qty:
            flash('Not enough stock for one or more items. Checkout aborted.')
            return redirect(url_for('view_cart'))
    total = 0.0
    items = []
    for pid, qty in pairs.items():
        cur = db.execute('SELECT name, price FROM products WHERE id=?', (pid,))
        p = cur.fetchone()
        line = p['price'] * qty
        total += line
        items.append({'id': pid, 'name': p['name'], 'qty': qty, 'unit': p['price'], 'line': line})
        db.execute('UPDATE products SET stock = stock - ? WHERE id=?', (qty, pid))
    db.execute('INSERT INTO sales (items_json, total) VALUES (?, ?)', (json.dumps(items), total))
    db.commit()
    resp = redirect(url_for('index'))
    resp.set_cookie('cart', '', expires=0)
    flash(f'Checkout successful. Total paid: {total:.2f}')
    return resp

@app.route('/admin', methods=['GET','POST'])
def admin():
    db = get_db(DATABASE)
    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price', 0))
        stock = int(request.form.get('stock', 0))
        if not name:
            flash('Name required.')
            return redirect(url_for('admin'))
        db.execute('INSERT INTO products (name, price, stock) VALUES (?, ?, ?)', (name, price, stock))
        db.commit()
        flash('Product added.')
        return redirect(url_for('admin'))
    cur = db.execute('SELECT id, name, price, stock FROM products')
    products = cur.fetchall()
    return render_template('admin.html', products=products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
