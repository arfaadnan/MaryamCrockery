import random
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .forms import ReviewForm
from .models import (
    Banner,
    Cart,
    CartItem,
    Category,
    InventoryHistory,
    Offer,
    Order,
    OrderItem,
    Product,
    Profile,
    Review,
    SiteSettings,
    SubCategory,
    Wishlist,
    WishlistItem,
    StoreSetting,
)

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .payment import (
    build_jazzcash_payload, verify_jazzcash_response,
    build_easypaisa_payload, verify_easypaisa_response,
)


def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    settings = StoreSetting.load() # Admin ki ki gayi settings uthao
    
    # HTML template ko data ke sath render karo
    html_string = render_to_string('store/pdf/dynamic_invoice.html', {
        'order': order,
        'settings': settings
    })
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.order_number}.pdf"'
    
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation error', status=500)
    return response

def download_shipping_label(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    settings = StoreSetting.load()
    
    html_string = render_to_string('store/pdf/dynamic_label.html', {
        'order': order,
        'settings': settings
    })
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="Label_{order.order_number}.pdf"'
    
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation error', status=500)
    return response




# ===============================
# HELPER FUNCTIONS
# ===============================
def _get_or_create_cart(request):
    """Utility helper to consistently retrieve or initialize a cart session."""
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart

# ===============================
# HOME
# ===============================
def home(request):
    context = {
        "banners": Banner.objects.filter(is_active=True),
        "categories": Category.objects.filter(is_active=True),
        "offers": Offer.objects.filter(is_active=True),
        "featured_products": Product.objects.filter(is_active=True, is_featured=True)[:8],
        "best_sellers": Product.objects.filter(is_active=True, is_best_seller=True)[:8],
    }
    return render(request, "store/home.html", context)


# ===============================
# SHOP
# ===============================
def shop(request):
    categories = Category.objects.filter(is_active=True).prefetch_related("subcategories")
    products = Product.objects.filter(is_active=True).select_related("category", "subcategory")

    category = request.GET.get("category")
    if category:
        products = products.filter(category__id=category)

    subcategory = request.GET.get("subcategory")
    if subcategory:
        products = products.filter(subcategory__id=subcategory)

    sort = request.GET.get("sort")
    sort_options = {
        "price_low": "price",
        "price_high": "-price",
        "bestselling": "-is_best_seller",
        "newest": "-created_at",
    }
    products = products.order_by(sort_options.get(sort, "-created_at"))

    paginator = Paginator(products, 9)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    context = {
        "products": products,
        "categories": categories,
        "selected_category": category,
        "selected_subcategory": subcategory,
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

    reviews = product.product_reviews.filter(is_approved=True).select_related("user")
    review_form = ReviewForm()
    existing_review = None

    if request.user.is_authenticated:
        existing_review = Review.objects.filter(product=product, user=request.user).first()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Please login to submit a review.")
            return redirect("store:login")

        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            if existing_review:
                messages.warning(request, "You have already reviewed this product.")
                return redirect("store:product_detail", slug=product.slug)

            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

            avg_rating = (
                product.product_reviews.filter(is_approved=True).aggregate(Avg("rating"))["rating__avg"] or 0
            )
            product.rating = round(avg_rating, 1)
            product.reviews = product.product_reviews.filter(is_approved=True).count()
            product.save()

            messages.success(request, "Your review has been submitted successfully.")
            return redirect("store:product_detail", slug=product.slug)

    context = {
        "product": product,
        "related_products": related_products,
        "reviews": reviews,
        "review_form": review_form,
        "existing_review": existing_review,
    }

    return render(request, "store/product_detail.html", context)


# ===============================
# CART & CHECKOUT
# ===============================
@require_POST
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    cart = _get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("store:cart")


@require_POST
def buy_now(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    cart = _get_or_create_cart(request)

    cart.items.all().delete()
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    return redirect("store:checkout")


def cart(request):
    cart = _get_or_create_cart(request)
    items = cart.items.select_related("product")
    total = sum(item.subtotal for item in items)

    context = {
        "cart": cart,
        "items": items,
        "total": total,
    }

    return render(request, "store/cart.html", context)


@require_POST
def increase_cart(request, item_id):
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.quantity += 1
    item.save()
    return redirect("store:cart")


@require_POST
def decrease_cart(request, item_id):
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    return redirect("store:cart")


@require_POST
def remove_cart(request, item_id):
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return redirect("store:cart")


def checkout(request):
    cart = _get_or_create_cart(request)
    items = cart.items.select_related("product")

    if not items.exists():
        messages.warning(request, "Aapka cart khali hai.")
        return redirect("store:cart")

    total = sum(item.subtotal for item in items)

    if request.method == "POST":
        order_number = f"MC{timezone.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

        with transaction.atomic():
            product_ids = [item.product_id for item in items]
            locked_products = {
                p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids)
            }

            out_of_stock_items = []
            for item in items:
                prod = locked_products[item.product_id]
                if prod.stock < item.quantity:
                    out_of_stock_items.append(
                        f"{prod.name} (Available: {prod.stock}, Requested: {item.quantity})"
                    )

            if out_of_stock_items:
                error_msg = "Kuch products out of stock hain: " + ", ".join(out_of_stock_items)
                messages.error(request, error_msg)
                return redirect("store:cart")

                order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                order_number=order_number,
                full_name=request.POST.get("full_name"),
                phone=request.POST.get("phone"),
                email=request.POST.get("email"),
                address=request.POST.get("address"),
                city=request.POST.get("city"),
                notes=request.POST.get("notes"),
                payment_method=request.POST.get("payment_method"),
                total=total,
                payment_status="Paid" if request.POST.get("payment_method") == "COD" else "Pending",
                payment_proof=request.FILES.get("payment_proof"),
            )

            for item in items:
                prod = locked_products[item.product_id]
                unit_price = getattr(prod, "final_price", prod.price)

                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    price=unit_price,
                    quantity=item.quantity,
                    subtotal=item.subtotal,
                )

                prod.stock -= item.quantity
                prod.save()

                InventoryHistory.objects.create(
                    product=prod,
                    quantity=-item.quantity,
                    note=f"Sold (Order {order.order_number})",
                )

            cart.items.all().delete()

        # ---- Notifications (order commit hone ke baad) ----
        site = SiteSettings.objects.first()
        admin_email = site.email if site and site.email else settings.DEFAULT_FROM_EMAIL

        # EMAIL: Customer
        if order.email:
            html_message = render_to_string(
                "emails/order_confirmation.html",
                {"order": order, "items": items},
            )
            plain_message = strip_tags(html_message)
            customer_email = EmailMultiAlternatives(
                subject=f"Order Confirmation - {order.order_number}",
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[order.email],
            )
            customer_email.attach_alternative(html_message, "text/html")
            customer_email.send(fail_silently=True)

        # EMAIL: Admin
        admin_subject = f"New Order Received - {order.order_number}"
        admin_body = (
            f"New order placed.\n\n"
            f"Order: {order.order_number}\n"
            f"Customer: {order.full_name}\n"
            f"Phone: {order.phone}\n"
            f"Email: {order.email}\n"
            f"City: {order.city}\n"
            f"Address: {order.address}\n"
            f"Payment: {order.payment_method}\n"
            f"Total: Rs. {order.total}"
        )
        EmailMultiAlternatives(
            subject=admin_subject,
            body=admin_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_email],
        ).send(fail_silently=True)

        # WhatsApp: Admin notification link
        wa_message = f"""🛍️ New Order Received

Order: {order.order_number}
Customer: {order.full_name}
Phone: {order.phone}
City: {order.city}
Total: Rs. {order.total}

Thank you for shopping with Maryam Crockery ❤️"""

        admin_whatsapp = site.whatsapp_number if site and site.whatsapp_number else "923223489220"
        request.session["order_whatsapp_link"] = f"https://wa.me/{admin_whatsapp}?text={quote(wa_message)}"

        if order.payment_method == "JazzCash":
            return redirect("store:jazzcash_start", order_id=order.id)
        elif order.payment_method == "EasyPaisa":
            return redirect("store:easypaisa_start", order_id=order.id)

        return redirect("store:order_success", order_id=order.id)

    return render(request, "store/checkout.html", {"items": items, "total": total, "site": SiteSettings.objects.first()})


# ===============================
# PAYMENT GATEWAY VIEWS
# ===============================

def start_jazzcash_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payload = build_jazzcash_payload(order)
    return render(request, "store/jazzcash_redirect.html", {
        "payload": payload,
        "post_url": settings.JAZZCASH_POST_URL,
    })


@csrf_exempt
@require_POST
def jazzcash_callback(request):
    post_data = request.POST.dict()

    if verify_jazzcash_response(post_data):
        order_number = post_data.get("pp_TxnRefNo")
        order = Order.objects.filter(order_number=order_number).first()
        if order:
            order.payment_status = "Paid"
            order.transaction_id = post_data.get("pp_RetreivalReferenceNo", "")
            order.gateway_response = str(post_data)
            order.save()
            return redirect("store:order_success", order_id=order.id)

    messages.error(request, "Payment verification failed. Please contact support.")
    return redirect("store:checkout")


def start_easypaisa_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payload = build_easypaisa_payload(order)
    return render(request, "store/easypaisa_redirect.html", {
        "payload": payload,
        "post_url": settings.EASYPAISA_POST_URL,
    })


@csrf_exempt
@require_POST
def easypaisa_callback(request):
    post_data = request.POST.dict()

    if verify_easypaisa_response(post_data):
        order_number = post_data.get("orderRefNum")
        order = Order.objects.filter(order_number=order_number).first()
        if order:
            order.payment_status = "Paid"
            order.transaction_id = post_data.get("transactionId", "")
            order.gateway_response = str(post_data)
            order.save()
            return redirect("store:order_success", order_id=order.id)

    messages.error(request, "Payment verification failed. Please contact support.")
    return redirect("store:checkout")


# ===============================
# SEARCH & AJAX ENDPOINTS
# ===============================
def search(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.filter(is_active=True)

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    context = {
        "products": products,
        "query": query,
    }
    return render(request, "store/search.html", context)


def live_search(request):
    """Naheed-style instant live search suggestions view"""
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True,
        )[:6]

        for product in products:
            image_url = product.image.url if getattr(product, "image", None) else ""
            price = float(getattr(product, "final_price", product.price))
            results.append({
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "price": price,
                "image": image_url,
            })

    return JsonResponse({"results": results})


@require_POST
def ajax_add_to_cart(request):
    """Add product to cart asynchronously without full page reload"""
    slug = request.POST.get("slug")
    product = get_object_or_404(Product, slug=slug, is_active=True)

    cart = _get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    cart_count = sum(item.quantity for item in cart.items.all())

    return JsonResponse({
        "status": "success",
        "message": f"{product.name} cart mein add kar diya gaya hai.",
        "cart_count": cart_count,
    })


def get_cart_drawer(request):
    """Renders data for off-canvas cart drawer"""
    cart = _get_or_create_cart(request)
    items = cart.items.select_related("product")
    total = sum(item.subtotal for item in items)

    item_list = []
    for item in items:
        image_url = item.product.image.url if getattr(item.product, "image", None) else ""
        price = float(getattr(item.product, "final_price", item.product.price))
        item_list.append({
            "id": item.id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price": price,
            "subtotal": float(item.subtotal),
            "image": image_url,
        })

    return JsonResponse({
        "items": item_list,
        "total": float(total),
        "count": sum(i.quantity for i in items),
    })


# ===============================
# USER ACCOUNTS & PROFILES
# ===============================
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("store:home")

        messages.error(request, "Invalid username or password.")

    return render(request, "store/login.html")


def user_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect("store:home")

    return render(request, "store/signup.html")


def user_logout(request):
    logout(request)
    return redirect("store:home")


@login_required
def profile(request):
    profile_obj, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name", "")
        request.user.last_name = request.POST.get("last_name", "")
        request.user.email = request.POST.get("email", "")

        profile_obj.phone = request.POST.get("phone", "")
        profile_obj.city = request.POST.get("city", "")
        profile_obj.address = request.POST.get("address", "")

        if request.FILES.get("profile_image"):
            profile_obj.profile_image = request.FILES["profile_image"]

        request.user.save()
        profile_obj.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("store:profile")

    return render(request, "store/profile.html", {"profile": profile_obj})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "store/my_orders.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "store/order_detail.html", {"order": order})


# ===============================
# WISHLIST & REVIEWS
# ===============================
def add_to_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    if request.user.is_authenticated:
        wishlist_obj, _ = Wishlist.objects.get_or_create(user=request.user)
    else:
        wishlist_obj, _ = Wishlist.objects.get_or_create(session_key=session_key)
    _, created = WishlistItem.objects.get_or_create(wishlist=wishlist_obj, product=product)

    if created:
        messages.success(request, "Product added to wishlist.")
    else:
        messages.info(request, "Product is already in your wishlist.")

    return redirect(request.META.get("HTTP_REFERER", "store:shop"))

def wishlist(request):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    if request.user.is_authenticated:
        wishlist_obj, _ = Wishlist.objects.get_or_create(user=request.user)
    else:
        wishlist_obj, _ = Wishlist.objects.get_or_create(session_key=session_key)
    items = wishlist_obj.items.select_related("product")

    return render(request, "store/wishlist.html", {"wishlist": wishlist_obj, "items": items})

@require_POST
def remove_wishlist(request, item_id):
    if not request.session.session_key:
        return redirect("store:wishlist")
    
    wishlist_obj = get_object_or_404(Wishlist, session_key=request.session.session_key)
    item = get_object_or_404(WishlistItem, id=item_id, wishlist=wishlist_obj)
    item.delete()
    messages.success(request, "Product removed from wishlist.")
    return redirect("store:wishlist")


@login_required
@require_POST
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    rating = request.POST.get("rating")
    review_text = request.POST.get("review")

    Review.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={
            "rating": rating,
            "review": review_text,
        },
    )
    messages.success(request, "Your review has been submitted successfully.")
    return redirect("store:product_detail", slug=product.slug)


# ===============================
# CATEGORIES & ADMIN/MISC
# ===============================
def contact(request):
    return render(request, "store/contact.html", {"site": SiteSettings.objects.first()})


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    whatsapp_link = request.session.pop("order_whatsapp_link", None)
    return render(request, "store/order_success.html", {"order": order, "whatsapp_link": whatsapp_link})


@staff_member_required
def low_stock_products(request):
    products = Product.objects.filter(stock__lte=5, is_active=True).order_by("stock")
    return render(request, "store/low_stock.html", {"products": products})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    subcategories = category.subcategories.filter(is_active=True)
    products = Product.objects.filter(category=category, is_active=True).select_related("subcategory")
    
    return render(
        request,
        "store/category_products.html",
        {"category": category, "subcategories": subcategories, "products": products},
    )


def subcategory_products(request, slug):
    subcategory = get_object_or_404(SubCategory, slug=slug, is_active=True)
    products = Product.objects.filter(
        subcategory=subcategory, is_active=True
    ).select_related("category", "subcategory")

    return render(
        request,
        "store/subcategory_products.html",
        {"subcategory": subcategory, "products": products},
    )


def load_subcategories(request):
    category_id = request.GET.get("category")
    subcategories = SubCategory.objects.filter(
        category_id=category_id, is_active=True
    ).values("id", "name")

    return JsonResponse(list(subcategories), safe=False)

###invoice

def render_pdf_view(request, order_id, template_path):
    order = get_object_or_404(Order, id=order_id)
    template = get_template(template_path)
    html = template.render({'order': order})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="document_{order.order_number}.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# Views for URLs
def invoice_pdf(request, order_id):
    return render_pdf_view(request, order_id, 'store/pdf/invoice.html')

def shipping_label_pdf(request, order_id):
    return render_pdf_view(request, order_id, 'store/pdf/shipping_label.html')