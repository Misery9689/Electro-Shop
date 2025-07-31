from django import template
from cart.cart import Cart

register = template.Library()

@register.simple_tag(takes_context=True)
def cart_total_amount(context):
    """Get total amount of items in cart"""
    request = context['request']
    cart = Cart(request)
    return cart.get_total_price()  # This now returns float

@register.simple_tag(takes_context=True)
def cart_total_items(context):
    """Get total number of items in cart"""
    request = context['request']
    cart = Cart(request)
    return len(cart)

@register.inclusion_tag('cart/cart_summary.html', takes_context=True)
def cart_summary(context):
    """Render cart summary"""
    request = context['request']
    cart = Cart(request)
    return {'cart': cart}

@register.filter
def multiply(value, arg):
    """Multiply two values"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def format_price(value):
    """Format price as currency"""
    try:
        return f"${float(value):.2f}"
    except (ValueError, TypeError):
        return "$0.00"
