from .models import Cart, Wishlist, Category, SiteSettings


def global_data(request):

    return {

        "categories": Category.objects.filter(is_active=True),

        "site_settings": SiteSettings.objects.first(),

    }


def navbar_counts(request):

    cart_count = 0
    wishlist_count = 0

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    try:

        cart = Cart.objects.get(session_key=session_key)

        cart_count = cart.items.count()

    except Cart.DoesNotExist:
        pass

    try:

        wishlist = Wishlist.objects.get(session_key=session_key)

        wishlist_count = wishlist.items.count()

    except Wishlist.DoesNotExist:
        pass

    return {

        "cart_count": cart_count,

        "wishlist_count": wishlist_count,

    }