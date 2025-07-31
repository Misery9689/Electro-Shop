from .cart import Cart

def cart_total_amount(request):
    """
    Context processor to make cart total available in templates
    """
    try:
        cart = Cart(request)
        return {'cart_total_amount': cart.get_total_price()}
    except:
        return {'cart_total_amount': 0}

def cart_context(request):
    """
    Context processor to make Cart object available in all templates
    """
    try:
        return {'cart_obj': Cart(request)}
    except:
        return {'cart_obj': None}
