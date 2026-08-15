from django.shortcuts import render, get_object_or_404

from .models import (
    Banner,
    Category,
    Offer,
    Product,
)

from django.shortcuts import redirect
from .models import Cart, CartItem

# ===============================
# HOME
# ===============================

def home(request):

    context = {

        "banners": Banner.objects.filter(is_active=True),

        "categories": Category.objects.filter(is_active=True),

        "offers": Offer.objects.filter(is_active=True),

        "featured_products": Product.objects.filter(
            is_active=True,
            is_featured=True
        )[:8],

        "best_sellers": Product.objects.filter(
            is_active=True,
            is_best_seller=True
        )[:8],

    }

    return render(
        request,
        "store/home.html",
        context
    )


# ===============================
# SHOP
# ===============================

def shop(request):

    products = Product.objects.filter(
        is_active=True
    ).select_related(
        "category",
        "subcategory"
    )

    categories = Category.objects.filter(
        is_active=True
    )

    context = {

        "products": products,

        "categories": categories,

    }

    return render(
        request,
        "store/shop.html",
        context
    )


# ===============================
# PRODUCT DETAIL
# ===============================

def product_detail(request, slug):

    product = get_object_or_404(

        Product,

        slug=slug,

        is_active=True

    )

    related_products = Product.objects.filter(

        category=product.category,

        is_active=True

    ).exclude(

        id=product.id

    )[:8]

    context = {

        "product": product,

        "related_products": related_products,

    }

    return render(

        request,

        "store/product_detail.html",

        context

    )
    
def add_to_cart(request, slug):

    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True
    )

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(
        session_key=session_key
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("store:cart")    

def cart(request):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(
        session_key=session_key
    )

    items = cart.items.select_related("product")

    total = sum(item.subtotal for item in items)

    context = {
        "cart": cart,
        "items": items,
        "total": total,
    }

    return render(
        request,
        "store/cart.html",
        context
    )
    
def increase_cart(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id
    )

    item.quantity += 1

    item.save()

    return redirect("store:cart")


def decrease_cart(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id
    )

    if item.quantity > 1:

        item.quantity -= 1

        item.save()

    return redirect("store:cart")


def remove_cart(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id
    )

    item.delete()

    return redirect("store:cart")    