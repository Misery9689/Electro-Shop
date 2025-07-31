from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from app.models import Category, Product, Order, OrderItem, Wishlist # Import new models
from django.contrib.auth import authenticate, login
from app.models import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from cart.cart import Cart
import json
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import transaction # Import transaction
from django.db.models import Count
from django.core.paginator import Paginator

def Master(request):
    return render(request, 'master.html')

def Index(request):
    category = Category.objects.all()
    # Get category filter from URL parameter
    category_id = request.GET.get('category')
    if category_id:
        try:
            # Filter products by category
            products = Product.objects.filter(category_id=category_id) # Changed to 'products'
            selected_category = Category.objects.get(id=category_id)
        except (Category.DoesNotExist, ValueError):
            # If invalid category_id, show all products
            products = Product.objects.all() # Changed to 'products'
            selected_category = None
    else:
        # Show all products if no category filter
        products = Product.objects.all() # Changed to 'products'
        selected_category = None
    context = {
        'category': category,
        'products': products, # Changed key from 'product' to 'products'
        'selected_category': selected_category,
    }
    return render(request, 'index.html', context)

@login_required
def profile_view(request):
    """Display user profile with all details"""
    user = request.user
    
    # Get user statistics
    wishlist_count = Wishlist.objects.filter(user=user).count()
    wishlist_items = Wishlist.objects.filter(user=user).select_related('product')[:5]  # Latest 5 items
    
    # Calculate wishlist total value
    wishlist_total = 0
    for item in wishlist_items:
        if item.product.price:
            wishlist_total += float(item.product.price)
    
    # Get order statistics using your existing Order model
    orders = Order.objects.filter(user=user)
    total_orders = orders.count()
    
    # Calculate total spent using your get_total_cost method
    total_spent = 0
    for order in orders:
        total_spent += float(order.get_total_cost())
    
    recent_orders = orders[:5]  # Latest 5 orders
    
    # Get payment method breakdown
    payment_method_counts = orders.values('payment_method').annotate(count=Count('payment_method'))
    
    # Get paid vs unpaid orders
    paid_orders = orders.filter(paid=True).count()
    unpaid_orders = orders.filter(paid=False).count()
    
    context = {
        'user': user,
        'wishlist_count': wishlist_count,
        'wishlist_items': wishlist_items,
        'wishlist_total': wishlist_total,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'recent_orders': recent_orders,
        'payment_method_counts': payment_method_counts,
        'paid_orders': paid_orders,
        'unpaid_orders': unpaid_orders,
        'user_since': user.date_joined,
    }
    
    return render(request, 'profile.html', context)

@login_required
def profile_edit(request):
    """Edit user profile information"""
    if request.method == 'POST':
        # Update user information
        user = request.user
        
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        
        # Validate email uniqueness
        if email != user.email and User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered with another account.')
            return redirect('profile_edit')
        
        # Update user fields
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile')
    
    return render(request, 'profile_edit.html', {'user': request.user})

@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep user logged in
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('profile')
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})

def Shop(request):
    category = Category.objects.all()
    # Get category filter from URL parameter
    category_id = request.GET.get('category')
    if category_id:
        try:
            # Filter products by category
            products = Product.objects.filter(category_id=category_id) # Changed to 'products'
            selected_category = Category.objects.get(id=category_id)
        except (Category.DoesNotExist, ValueError):
            # If invalid category_id, show all products
            products = Product.objects.all() # Changed to 'products'
            selected_category = None
    else:
        # Show all products if no category filter
        products = Product.objects.all() # Changed to 'products'
        selected_category = None
        
    paginator = Paginator(products, 12) # Show 12 products per page
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    # Sorting logic (from your original template)
    sort_by_option = request.GET.get('sort_by', 'relevance')
    if sort_by_option == 'name-asc':
        products = products.order_by('name')
    elif sort_by_option == 'name-desc':
        products = products.order_by('-name')
    elif sort_by_option == 'price-asc':
        products = products.order_by('price')
    elif sort_by_option == 'price-desc':
        products = products.order_by('-price')
    # Add more sorting options as needed for rating, etc.

    context = {
        'category': category,
        'products': products_page, # Pass the paginated products
        'selected_category': selected_category,
        'sort_by_option': sort_by_option,
        'view_mode': request.GET.get('view_mode', 'grid'), # Default to grid if not specified
    }
    return render(request, 'shop.html', context)

def Blog(request):
    return render(request, 'blog.html')

@login_required(login_url='/login/')
def CheckOut(request):
    cart = Cart(request)
    if not cart:
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('cart_detail')
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        payment_method = request.POST.get('payment_method', 'Cash on Delivery') # Default to COD
        if not shipping_address:
            messages.error(request, "Shipping address is required to place an order.")
            return redirect('checkout')
        try:
            with transaction.atomic(): # Ensure atomicity for order creation
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=shipping_address,
                    payment_method=payment_method,
                    total_price=cart.get_total_price(),
                    paid=False, # Orders are initially unpaid, unless integrated with a payment gateway
                    name=request.POST.get('name'),
                    phone=request.POST.get('phone'),
                    email=request.POST.get('email')
                )
                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        price=item['price'],
                        quantity=item['quantity']
                    )
                cart.clear() # Clear the cart after successful order creation
                messages.success(request, "Your order has been placed successfully!")
                return redirect('order_success', order_id=order.id)
        except Exception as e:
            messages.error(request, f"There was an error placing your order: {e}")
            return redirect('checkout')
    else:
        cart_items = []
        for item in cart:
            item_total = item['price'] * item['quantity']
            item['total'] = item_total
            cart_items.append(item)
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'cart_count': len(cart),
            'cart_total': cart.get_total_price(),
        }
        return render(request, 'checkout.html', context)

def AboutUs(request):
    return render(request, 'about_us.html')

# MODIFIED: Login view to correctly use AuthenticationForm
def Login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.") # Form validation failed
    else:
        form = AuthenticationForm()
    context = {'form': form}
    return render(request, 'Registration/login.html', context)

def Register(request):
    return render(request, 'register.html')

# RENAME THIS FUNCTION - this was causing the conflict!


def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product
    }
    return render(request, 'detail.html', context)

def Contact(request):
    return render(request, 'contact.html')

def Signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password') # Use password directly from cleaned_data
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Registration successful! You are now logged in.")
                return redirect('index') # Redirect to index after successful signup and login
            else:
                messages.error(request, "Authentication failed after registration.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    context = {'form': form}
    return render(request, 'Registration/signup.html', context)

@login_required(login_url='/accounts/login/')
def cart_add(request, id):
    try:
        product = get_object_or_404(Product, id=id)
        cart = Cart(request)
        cart.add(product=product)
        messages.success(request, f'{product.name} has been added to your cart!')
        return redirect('cart_detail')
    except Exception as e:
        messages.error(request, 'Error adding item to cart. Please try again.')
        print(f"Error in cart_add: {e}")
        return redirect("index")

@login_required(login_url='/login/')
def item_clear(request, id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=id)
        cart.remove(product)
        messages.success(request, f'Item has been removed from your cart!')
        return redirect("cart_detail")
    except Exception as e:
        messages.error(request, 'Error removing item from cart.')
        return redirect("cart_detail")

@login_required(login_url='/login/')
def item_increment(request, id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=id)
        cart.add(product=product)
        return redirect("cart_detail")
    except Exception as e:
        messages.error(request, 'Error updating cart.')
        return redirect("cart_detail")

@login_required(login_url='/login/')
def item_decrement(request, id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=id)
        cart.decrement(product=product)
        return redirect("cart_detail")
    except Exception as e:
        messages.error(request, 'Error updating cart.')
        return redirect("cart_detail")

@login_required(login_url='/login/')
def cart_clear(request):
    try:
        cart = Cart(request)
        cart.clear()
        messages.success(request, 'Your cart has been cleared!')
        return redirect("cart_detail")
    except Exception as e:
        messages.error(request, 'Error clearing cart.')
        return redirect("cart_detail")

@login_required(login_url='/login/')
def cart_detail(request):
    try:
        cart = Cart(request)
        cart_items = []
        for item in cart:
            item_total = item['price'] * item['quantity']
            item['total'] = item_total
            cart_items.append(item)
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'cart_count': len(cart),
            'cart_total': cart.get_total_price(),
        }
        return render(request, 'cart/cart_detail.html', context)
    except Exception as e:
        print(f"Error in cart_detail: {e}")
        import traceback
        traceback.print_exc()
        # Clear the cart if there's an error
        try:
            request.session['cart'] = {}
            request.session.modified = True
        except:
            pass
        context = {
            'cart': Cart(request),
            'cart_items': [],
            'cart_count': 0,
            'cart_total': 0.0,
        }
        return render(request, 'cart/cart_detail.html', context)
    

@login_required
def order_history(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'order_history.html', context)

@login_required
def order_detail(request, order_id):
    """Display detailed view of a specific order"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order_items = OrderItem.objects.filter(order=order).select_related('product')
        
        context = {
            'order': order,
            'order_items': order_items,
        }
        
        return render(request, 'order_detail.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('order_history')

# Function to create a sample order (for testing) - updated for your model
@login_required
def create_sample_order(request):
    """Create a sample order for testing purposes"""
    if request.method == 'POST':
        # Get some products for the sample order
        products = Product.objects.all()[:3]  # Get first 3 products
        
        if products:
            # Create order using your model structure
            order = Order.objects.create(
                user=request.user,
                paid=True,  # Set as paid for demo
                shipping_address="123 Sample Street, Sample City, 12345",
                payment_method="Cash on Delivery",
                name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                phone="123-456-7890",
                email=request.user.email,
            )
            
            # Create order items and calculate total
            total_cost = 0
            for product in products:
                if product.price:
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=1,
                        price=product.price
                    )
                    total_cost += float(order_item.get_cost())
            
            # Update the total_price field
            order.total_price = total_cost
            order.save()
            
            messages.success(request, f'Sample order #{order.id} created successfully!')
        else:
            messages.error(request, 'No products available to create sample order.')
    
    return redirect('profile')

# New View for Order Success Page
@login_required(login_url='/login/')
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order
    }
    return render(request, 'order_success.html', context)

# New View for User Orders List
@login_required(login_url='/login/')
def user_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    context = {
        'orders': orders
    }
    return render(request, 'order_list.html', context)

@login_required
def wishlist_add(request, product_id):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if item already exists in wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f'{product.name} added to your wishlist!')
    else:
        messages.info(request, f'{product.name} is already in your wishlist!')
    
    # If it's an AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to wishlist!' if created else f'{product.name} is already in wishlist!',
            'wishlist_count': wishlist_count,
            'created': created
        })
    
    # For regular requests, redirect to the previous page or home
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def wishlist_remove(request, product_id):
    """Remove product from wishlist"""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        messages.success(request, f'{product.name} removed from your wishlist!')
        
        # If it's an AJAX request, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
            return JsonResponse({
                'success': True,
                'message': f'{product.name} removed from wishlist!',
                'wishlist_count': wishlist_count
            })
            
    except Wishlist.DoesNotExist:
        messages.error(request, 'Item not found in your wishlist!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Item not found in wishlist!'
            })
    
    # For regular requests, redirect to wishlist or previous page
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))


# AJAX version for better user experience (optional)
@login_required
def wishlist_toggle_ajax(request, product_id):
    """Toggle product in wishlist via AJAX"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if not created:
            wishlist_item.delete()
            in_wishlist = False
            message = f'{product.name} removed from wishlist'
        else:
            in_wishlist = True
            message = f'{product.name} added to wishlist'
        
        return JsonResponse({
            'success': True,
            'in_wishlist': in_wishlist,
            'message': message
        })
    
    return JsonResponse({'success': False})

@login_required
def wishlist_view(request):
    """Display user's wishlist with enhanced features"""
    try:
        wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
        
        # Calculate total value properly
        total_value = 0
        for item in wishlist_items:
            if item.product.price:
                total_value += float(item.product.price)
        
        context = {
            'wishlist_items': wishlist_items,
            'total_value': total_value,
        }
        return render(request, 'wishlist.html', context)
    except Exception as e:
        messages.error(request, f'Error loading wishlist: {str(e)}')
        context = {
            'wishlist_items': [],
            'total_value': 0,
        }
        return render(request, 'wishlist.html', context)
    
@login_required
def wishlist_add_all_to_cart(request):
    """Add all wishlist items to cart"""
    if request.method == 'POST':
        try:
            wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
            
            if not wishlist_items:
                messages.info(request, 'Your wishlist is empty!')
                return redirect('wishlist')
            
            cart = Cart(request)
            added_count = 0
            
            for item in wishlist_items:
                cart.add(product=item.product)
                added_count += 1
            
            messages.success(request, f'{added_count} item{"s" if added_count != 1 else ""} added to cart!')
            return redirect('cart_detail')
            
        except Exception as e:
            messages.error(request, f'Error adding items to cart: {str(e)}')
            return redirect('wishlist')
    
    return redirect('wishlist')