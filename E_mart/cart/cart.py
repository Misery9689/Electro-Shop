from decimal import Decimal
from app.models import Product

class Cart:
    def __init__(self, request):
        """
        Initialize the cart using session storage
        """
        self.session = request.session
        self.request = request
        
        # Use 'cart' as the session key
        cart = self.session.get('cart')
        if not cart:
            # Save an empty cart in the session
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        ONLY store basic data types - NO objects!
        """
        product_id = str(product.id)
        
        if product_id not in self.cart:
            # ONLY store JSON-serializable data - NO Product objects!
            self.cart[product_id] = {
                'quantity': 0,
                'price': float(product.price),  # Convert to float
                'name': str(product.name),      # Ensure it's a string
                'product_id': int(product.id),  # Ensure it's an int
            }
            # Add image URL if available
            if product.image:
                self.cart[product_id]['image'] = str(product.image.url)
            else:
                self.cart[product_id]['image'] = None

        if override_quantity:
            self.cart[product_id]['quantity'] = int(quantity)
        else:
            self.cart[product_id]['quantity'] += int(quantity)
        
        self.save()

    def save(self):
        """Mark the session as modified to make sure it gets saved"""
        # Clean the cart data before saving to ensure no objects are stored
        cleaned_cart = {}
        for product_id, item in self.cart.items():
            cleaned_cart[str(product_id)] = {
                'quantity': int(item.get('quantity', 0)),
                'price': float(item.get('price', 0)),
                'name': str(item.get('name', '')),
                'product_id': int(item.get('product_id', 0)),
                'image': str(item.get('image', '')) if item.get('image') else None
            }
        
        self.session['cart'] = cleaned_cart
        self.cart = cleaned_cart
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def decrement(self, product):
        """
        Decrement the quantity of a product in the cart.
        If quantity becomes 0, remove the product.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            if self.cart[product_id]['quantity'] > 1:
                self.cart[product_id]['quantity'] -= 1
                self.save()
            else:
                self.remove(product)

    def __iter__(self):
        """
        Iterate through the items in the cart and get the products
        from the database. NEVER store Product objects in session!
        """
        product_ids = [item['product_id'] for item in self.cart.values()]
        
        # Get the product objects from database
        products = Product.objects.filter(id__in=product_ids)
        products_dict = {product.id: product for product in products}
        
        # Yield items with product data (but don't store Product objects)
        for item in self.cart.values():
            product_id = item['product_id']
            if product_id in products_dict:
                product = products_dict[product_id]
                yield {
                    'product_id': product_id,
                    'name': item['name'],
                    'price': float(item['price']),
                    'quantity': int(item['quantity']),
                    'total_price': float(item['price']) * int(item['quantity']),
                    'image': item.get('image'),
                    'product': product  # Only add for template use, not stored in session
                }

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(int(item['quantity']) for item in self.cart.values())

    def get_total_price(self):
        """
        Get the total price of all items in the cart.
        """
        total = sum(
            float(item['price']) * int(item['quantity'])
            for item in self.cart.values()
        )
        return round(total, 2)

    def clear(self):
        """
        Remove cart from session
        """
        if 'cart' in self.session:
            del self.session['cart']
            self.session.modified = True

    def get_item_count(self):
        """
        Get the total number of different items in the cart.
        """
        return len(self.cart)

    def is_empty(self):
        """
        Check if cart is empty
        """
        return len(self.cart) == 0
