
import json
import uuid
from datetime import datetime

class GroceryStore:
    def __init__(self, data_file='data.json'):
        self.data_file = data_file
        self._load()
        self.cart = {}

    def _load(self):
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {'products': {}, 'sales': []}
        self.products = data.get('products', {})
        self.sales = data.get('sales', [])

    def _save(self):
        with open(self.data_file, 'w') as f:
            json.dump({'products': self.products, 'sales': self.sales}, f, indent=2)

    def list_products(self):
        if not self.products:
            print('No products available.')
            return
        print('\nAvailable Products:')
        print('{:<8} {:<20} {:>8} {:>8}'.format('ID','Name','Price','Stock'))
        for pid, p in self.products.items():
            print('{:<8} {:<20} {:>8.2f} {:>8}'.format(pid, p['name'], p['price'], p['stock']))

    def add_product(self, name, price, stock):
        pid = str(uuid.uuid4())[:8]
        self.products[pid] = {'name': name, 'price': price, 'stock': stock}
        self._save()
        print(f'Product "{name}" added with id {pid}.')

    def add_to_cart(self, pid, qty=1):
        if pid not in self.products:
            print('Invalid product id.')
            return
        if qty <= 0:
            print('Quantity must be >= 1.')
            return
        if self.products[pid]['stock'] < qty:
            print('Not enough stock.')
            return
        self.cart[pid] = self.cart.get(pid, 0) + qty
        print(f'Added {qty} x {self.products[pid]["name"]} to cart.')

    def view_cart(self):
        if not self.cart:
            print('Cart is empty.')
            return
        print('\nYour Cart:')
        total = 0.0
        print('{:<8} {:<20} {:>8} {:>10}'.format('ID','Name','Qty','Line Total'))
        for pid, qty in self.cart.items():
            p = self.products.get(pid)
            line = p['price'] * qty
            total += line
            print('{:<8} {:<20} {:>8} {:>10.2f}'.format(pid, p['name'], qty, line))
        print(f'\nTotal: {total:.2f}')

    def remove_from_cart(self, pid):
        if pid in self.cart:
            del self.cart[pid]
            print('Item removed from cart.')
        else:
            print('Item not in cart.')

    def checkout(self):
        if not self.cart:
            print('Cart is empty.')
            return
        total = 0.0
        items = []
        for pid, qty in self.cart.items():
            p = self.products[pid]
            if p['stock'] < qty:
                print(f'Not enough stock for {p["name"]}. Checkout aborted.')
                return
            line = p['price'] * qty
            total += line
            items.append({'id': pid, 'name': p['name'], 'qty': qty, 'unit_price': p['price'], 'line_total': line})
        # reduce stock
        for it in items:
            self.products[it['id']]['stock'] -= it['qty']
        sale = {
            'sale_id': str(uuid.uuid4())[:8],
            'timestamp': datetime.now().isoformat(),
            'items': items,
            'total': total
        }
        self.sales.append(sale)
        self._save()
        print('\n--- Receipt ---')
        for it in items:
            print(f"{it['qty']} x {it['name']} @ {it['unit_price']:.2f} = {it['line_total']:.2f}")
        print(f'Total payable: {total:.2f}')
        print('Thank you for shopping!')
        self.cart = {}
