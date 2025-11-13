
from store import GroceryStore

def main():
    store = GroceryStore(data_file='data.json')
    while True:
        print('\n=== Grocery Store Application ===')
        print('1. View products')
        print('2. Add product to cart')
        print('3. View cart')
        print('4. Remove item from cart')
        print('5. Checkout')
        print('6. Add new product (admin)')
        print('7. Exit')
        choice = input('Choose an option: ').strip()
        if choice == '1':
            store.list_products()
        elif choice == '2':
            pid = input('Enter product id to add: ').strip()
            qty = int(input('Quantity: ').strip() or 1)
            store.add_to_cart(pid, qty)
        elif choice == '3':
            store.view_cart()
        elif choice == '4':
            pid = input('Enter product id to remove: ').strip()
            store.remove_from_cart(pid)
        elif choice == '5':
            store.checkout()
        elif choice == '6':
            name = input('Product name: ').strip()
            price = float(input('Price (e.g. 49.99): ').strip())
            stock = int(input('Stock quantity: ').strip())
            store.add_product(name, price, stock)
        elif choice == '7':
            print('Goodbye!')
            break
        else:
            print('Invalid choice. Try again.')

if __name__ == '__main__':
    main()
