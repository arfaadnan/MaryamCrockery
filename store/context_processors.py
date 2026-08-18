from .models import Cart, Wishlist, SiteSettings, Category


def global_data(request):
    """
    Site settings aur dynamic categories har page par available hongi.
    """
    site_settings = SiteSettings.objects.first()
    # Dynamic header menu ke liye top categories
    categories = Category.objects.all()

    return {
        "site_settings": site_settings,
        "categories": categories,
    }


def navbar_counts(request):
    """
    Session-based aur Authenticated User dono ke liye Cart aur Wishlist counts.
    """
    cart_count = 0
    wishlist_count = 0
    wishlist_products = []

    # Cart Count Logic
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        wishlist = Wishlist.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        cart = Cart.objects.filter(session_key=session_key).first() if session_key else None
        wishlist = Wishlist.objects.filter(session_key=session_key).first() if session_key else None

    # Fetch Cart Items Count
    if cart:
        cart_count = cart.items.count()

    # Fetch Wishlist Count & IDs
    if wishlist:
        wishlist_count = wishlist.items.count()
        wishlist_products = list(
            wishlist.items.values_list("product_id", flat=True)
        )

    return {
        "cart_count": cart_count,
        "wishlist_count": wishlist_count,
        "wishlist_products": wishlist_products,
    }