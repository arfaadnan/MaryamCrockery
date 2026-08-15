from django.shortcuts import render, get_object_or_404

from .models import Category, Product, Cart, CartItem, Order, OrderItem, SiteSettings
from django.shortcuts import redirect
from .models import Cart, CartItem
from django.utils import timezone
import random
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# ===============================
# HOME
# ===============================


def home(request):

    context = {
        "banners": Banner.objects.filter(is_active=True),
        "categories": Category.objects.filter(is_active=True),
        "offers": Offer.objects.filter(is_active=True),
        "featured_products": Product.objects.filter(is_active=True, is_featured=True)[
            :8
        ],
        "best_sellers": Product.objects.filter(is_active=True, is_best_seller=True)[:8],
    }

    return render(request, "store/home.html", context)


# ===============================
# SHOP
# ===============================


def shop(request):

    products = Product.objects.filter(is_active=True).select_related(
        "category", "subcategory"
    )

    categories = Category.objects.filter(is_active=True)

    # Category Filter
    category_id = request.GET.get("category")

    if category_id:
        products = products.filter(category_id=category_id)

    # Sorting
    sort = request.GET.get("sort")

    if sort == "low":
        products = products.order_by("price")

    elif sort == "high":
        products = products.order_by("-price")

    else:
        products = products.order_by("-created_at")

    # Pagination
    paginator = Paginator(products, 9)

    page_number = request.GET.get("page")

    products = paginator.get_page(page_number)

    context = {
        "products": products,
        "categories": categories,
        "selected_category": category_id,
        "selected_sort": sort,
    }

    return render(request, "store/shop.html", context)


# ===============================
# PRODUCT DETAIL
# ===============================


def product_detail(request, slug):

    product = get_object_or_404(Product, slug=slug, is_active=True)

    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:8]

    context = {
        "product": product,
        "related_products": related_products,
    }

    return render(request, "store/product_detail.html", context)


def add_to_cart(request, slug):

    product = get_object_or_404(Product, slug=slug, is_active=True)

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(session_key=session_key)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("store:cart")


def cart(request):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(session_key=session_key)

    items = cart.items.select_related("product")

    total = sum(item.subtotal for item in items)

    context = {
        "cart": cart,
        "items": items,
        "total": total,
    }

    return render(request, "store/cart.html", context)


def increase_cart(request, item_id):

    item = get_object_or_404(CartItem, id=item_id)

    item.quantity += 1

    item.save()

    return redirect("store:cart")


def decrease_cart(request, item_id):

    item = get_object_or_404(CartItem, id=item_id)

    if item.quantity > 1:

        item.quantity -= 1

        item.save()

    return redirect("store:cart")


def remove_cart(request, item_id):

    item = get_object_or_404(CartItem, id=item_id)

    item.delete()

    return redirect("store:cart")


def checkout(request):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(session_key=session_key)

    items = cart.items.select_related("product")

    if not items.exists():
        return redirect("store:cart")

    total = sum(item.subtotal for item in items)

    if request.method == "POST":

        order_number = (
            f"MC{timezone.now().strftime('%Y%m%d')}" f"{random.randint(1000,9999)}"
        )

        order = Order.objects.create(
            order_number=order_number,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            notes=request.POST.get("notes"),
            payment_method=request.POST.get("payment_method"),
            total=total,
        )

        for item in items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.final_price,
                quantity=item.quantity,
                subtotal=item.subtotal,
            )

        cart.items.all().delete()

        return redirect("store:order_success")

    context = {
        "cart": cart,
        "items": items,
        "total": total,
    }

    return render(
        request,
        "store/checkout.html",
        context,
    )


def order_success(request):

    return render(
        request,
        "store/order_success.html",
    )


def contact(request):

    context = {
        "site": SiteSettings.objects.first(),
    }

    return render(
        request,
        "store/contact.html",
        context,
    )


def search(request):

    query = request.GET.get("q", "")

    products = Product.objects.filter(is_active=True)

    if query:

        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    context = {
        "products": products,
        "query": query,
    }

    return render(
        request,
        "store/search.html",
        context,
    )


def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")

        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user:

            login(request, user)

            return redirect("store:home")

        messages.error(request, "Invalid username or password.")

    return render(
        request,
        "store/login.html",
    )


def user_signup(request):

    if request.method == "POST":

        username = request.POST.get("username")

        email = request.POST.get("email")

        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():

            messages.error(request, "Username already exists.")

        else:

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )

            login(
                request,
                user,
            )

            return redirect("store:home")

    return render(
        request,
        "store/signup.html",
    )

def user_logout(request):

    logout(request)

    return redirect("store:home")