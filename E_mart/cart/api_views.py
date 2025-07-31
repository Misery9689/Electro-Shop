from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from app.models import Product # Assuming Product model is in 'app' app

class CartViewSet(viewsets.GenericViewSet): # Use GenericViewSet for more control over methods
    serializer_class = CartSerializer

    def get_object(self):
        """
        Helper method to get or create the current user's/session's cart,
        and handle merging anonymous carts into authenticated ones.
        Includes print statements for debugging.
        """
        user = self.request.user
        session_key = self.request.session.session_key

        print(f"\n--- get_object called ---")
        print(f"Request User: {user.username if user.is_authenticated else 'Anonymous'}")
        print(f"Request Session Key (initial): {session_key}")

        # Ensure session key exists for anonymous users
        if not user.is_authenticated and not session_key:
            self.request.session.save()
            session_key = self.request.session.session_key
            print(f"New Session Key generated for anonymous user: {session_key}")

        user_cart = None
        if user.is_authenticated:
            user_cart = Cart.objects.filter(user=user).first()
            print(f"Authenticated Cart (user={user.username}): {user_cart.pk if user_cart else 'None'}")

        session_cart = None
        if session_key:
            session_cart = Cart.objects.filter(session_key=session_key).first()
            print(f"Session Cart (session_key={session_key}): {session_cart.pk if session_cart else 'None'}")

        # --- Cart Retrieval and Merging Logic ---
        if user.is_authenticated:
            if user_cart and session_cart and user_cart.pk != session_cart.pk:
                # Scenario 1: User logged in, has an existing authenticated cart AND an anonymous cart for current session
                print(f"MERGING: Anonymous cart {session_cart.pk} into authenticated cart {user_cart.pk}")
                for item in session_cart.items.all():
                    existing_item = CartItem.objects.filter(cart=user_cart, product=item.product).first()
                    if existing_item:
                        existing_item.quantity += item.quantity
                        existing_item.save()
                        print(f"  Merged existing item: {item.product.name} (new quantity: {existing_item.quantity})")
                    else:
                        item.cart = user_cart
                        item.save()
                        print(f"  Moved new item: {item.product.name}")
                session_cart.delete() # Delete the anonymous cart after merging
                print(f"Anonymous cart {session_cart.pk} deleted.")
                return user_cart
            elif user_cart:
                # Scenario 2: User logged in, has an authenticated cart, no anonymous cart or already merged
                print(f"RETURNING: Existing authenticated cart {user_cart.pk}")
                return user_cart
            elif session_cart:
                # Scenario 3: User logged in, but only has an anonymous cart for current session (first login or new session)
                print(f"LINKING: Anonymous cart {session_cart.pk} to authenticated user {user.username}")
                session_cart.user = user
                session_cart.session_key = None # Clear session key as it's now linked to user
                session_cart.save()
                return session_cart
            else:
                # Scenario 4: User logged in, has no existing cart (neither authenticated nor anonymous)
                print(f"CREATING: New cart for authenticated user {user.username}")
                return Cart.objects.create(user=user)
        else: # Anonymous user
            if session_cart:
                # Scenario 5: Anonymous user has an existing cart for this session
                print(f"RETURNING: Existing anonymous cart {session_cart.pk}")
                return session_cart
            else:
                # Scenario 6: Anonymous user has no cart for this session, create a new one
                print(f"CREATING: New anonymous cart for session {session_key}")
                return Cart.objects.create(session_key=session_key)

    def list(self, request, *args, **kwargs):
        """
        Handles GET requests to /api/v1/cart/
        Returns the current user's cart, creating it if it doesn't exist,
        and handling merging if necessary.
        """
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    # The custom actions below will now correctly use the cart retrieved by get_object()

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self.get_object() # Get the current user's cart
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity, 'price': product.price} # Store price at time of adding
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = self.get_serializer(cart) # Return the whole updated cart
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart = self.get_object() # Get the current user's cart
        product_id = request.data.get('product_id')

        try:
            product = Product.objects.get(id=product_id)
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()
            serializer = self.get_serializer(cart) # Return the updated cart
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (Product.DoesNotExist, CartItem.DoesNotExist):
            return Response({'detail': 'Item not found in cart.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def update_item_quantity(self, request):
        cart = self.get_object() # Get the current user's cart
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        if quantity <= 0:
            return Response({'detail': 'Quantity must be positive.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity = quantity
            cart_item.save()
            serializer = self.get_serializer(cart) # Return the updated cart
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not in cart.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def clear_cart(self, request):
        cart = self.get_object() # Get the current user's cart
        cart.items.all().delete()
        serializer = self.get_serializer(cart) # Return the cleared cart
        return Response(serializer.data, status=status.HTTP_200_OK)
