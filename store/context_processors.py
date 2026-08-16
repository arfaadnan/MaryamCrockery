from .models import Cart, Wishlist, SiteSettings


def global_data(request):

    site_settings = SiteSettings.objects.first()

    return {
        "site_settings": site_settings,
    }


def navbar_counts(request):

    cart_count = 0
    wishlist_count = 0
    wishlist_products = []

    if request.session.session_key:

        session_key = request.session.session_key

        try:
            cart = Cart.objects.get(session_key=session_key)
            cart_count = cart.items.count()

        except Cart.DoesNotExist:
            pass

        try:
            wishlist = Wishlist.objects.get(session_key=session_key)

            wishlist_count = wishlist.items.count()

            wishlist_products = list(
                wishlist.items.values_list(
                    "product_id",
                    flat=True,
                )
            )

        except Wishlist.DoesNotExist:
            pass

    return {
        "cart_count": cart_count,
        "wishlist_count": wishlist_count,
        "wishlist_products": wishlist_products,
    }