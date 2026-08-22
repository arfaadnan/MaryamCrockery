from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)

from .models import (
    Banner,
    Offer,
    InstagramPost,
)

from .models import StoreSetting, SiteSetting

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

from django.contrib import messages

from django.db import transaction
from django.db.models import (
    Count,
    Sum,
    F,
    Max,
)

from django.http import JsonResponse

from django.utils import timezone

# STORE MODELS

from store.models import (
    Product,
    Order,
    OrderItem,
    InventoryHistory,
    Category,
    SubCategory,
    ProductImage,
    ProductReturn,
    SiteSettings,
)

# ============================================
# AUTH — LOGIN / LOGOUT
# ============================================

def manager_login(request):

    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            # Sirf manager dashboard access

            if user.is_staff or user.is_superuser:

                login(request, user)

                return redirect("dashboard:home")

            else:

                messages.error(request, "Aap ko manager access nahi hai.")

        else:

            messages.error(request, "Username ya password ghalat hai.")

    return render(request, "dashboard/login.html")

@login_required
def manager_logout(request):

    logout(request)

    return redirect("dashboard:login")


# ============================================
# DASHBOARD HOME
# ============================================

@login_required
def dashboard_home(request):

    # Dashboard Statistics

    total_products = Product.objects.count()

    total_orders = Order.objects.count()

    total_categories = Category.objects.count()

    # Today's Sale

    today = timezone.now().date()

    today_sale = (
        Order.objects.filter(created_at__date=today, payment_status="Paid").aggregate(
            total=Sum("total")
        )["total"]
        or 0
    )

    # Total Sale

    total_sale = (
        Order.objects.filter(payment_status="Paid").aggregate(total=Sum("total"))[
            "total"
        ]
        or 0
    )

    # Pending Payment

    pending_payment = (
        Order.objects.filter(payment_status="Pending").aggregate(total=Sum("total"))[
            "total"
        ]
        or 0
    )

    # Paid Orders Count

    paid_orders = Order.objects.filter(payment_status="Paid").count()

    # Order Status Count

    pending_orders = Order.objects.filter(status="Pending").count()

    confirmed_orders = Order.objects.filter(status="Confirmed").count()

    shipped_orders = Order.objects.filter(status="Shipped").count()

    delivered_orders = Order.objects.filter(status="Delivered").count()

    # Low Stock Count

    low_stock = Product.objects.filter(stock__lte=F("low_stock_limit")).count()

    # Recent Orders

    recent_orders = Order.objects.all().order_by("-created_at")[:5]

    # Low Stock Products

    low_stock_products = Product.objects.filter(stock__lte=F("low_stock_limit"))[:5]

    # Material Wise Stock

    material_stock = (
        Product.objects.values("material")
        .annotate(total_products=Count("id"), total_stock=Sum("stock"))
        .order_by("-total_stock")
    )

    # Cash Report

    now = timezone.now()

    month_sale = (
        Order.objects.filter(
            created_at__year=now.year,
            created_at__month=now.month,
            payment_status="Paid",
        ).aggregate(total=Sum("total"))["total"]
        or 0
    )

    cod_sale = (
        Order.objects.filter(payment_method="COD", payment_status="Paid").aggregate(
            total=Sum("total")
        )["total"]
        or 0
    )

    online_sale = (
        Order.objects.filter(
            payment_method__in=["JazzCash", "EasyPaisa", "Bank"], payment_status="Paid"
        ).aggregate(total=Sum("total"))["total"]
        or 0
    )

    context = {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_categories": total_categories,
        "today_sale": today_sale,
        "total_sale": total_sale,
        "pending_payment": pending_payment,
        "paid_orders": paid_orders,
        "pending_orders": pending_orders,
        "confirmed_orders": confirmed_orders,
        "shipped_orders": shipped_orders,
        "delivered_orders": delivered_orders,
        "low_stock": low_stock,
        "recent_orders": recent_orders,
        "low_stock_products": low_stock_products,
        "material_stock": material_stock,
        "month_sale": month_sale,
        "cod_sale": cod_sale,
        "online_sale": online_sale,
    }

    return render(request, "dashboard/dashboard.html", context)


# ============================================
# PRODUCTS
# ============================================

@login_required
def product_list(request):

    products = Product.objects.all()

    return render(request, "dashboard/products/list.html", {"products": products})

@login_required
def product_add(request):

    categories = Category.objects.all()

    if request.method == "POST":

        product = Product.objects.create(
            category_id=request.POST.get("category"),
            name=request.POST.get("name"),
            sku=request.POST.get("sku"),
            price=request.POST.get("price"),
            stock=request.POST.get("stock"),
            description=request.POST.get("description"),
            main_image=request.FILES.get("main_image"),
        )

        gallery_images = request.FILES.getlist("gallery")

        for image in gallery_images:

            ProductImage.objects.create(product=product, image=image)

        return redirect("dashboard:products")

    return render(request, "dashboard/products/add.html", {"categories": categories})


# ============================
# PRODUCT EDIT
# ============================

@login_required
def product_edit(request, id):

    product = get_object_or_404(Product, id=id)

    categories = Category.objects.all()

    subcategories = SubCategory.objects.filter(category=product.category)

    if request.method == "POST":

        product.name = request.POST.get("name")

        product.sku = request.POST.get("sku")

        product.category_id = request.POST.get("category")

        product.subcategory_id = request.POST.get("subcategory")

        product.price = request.POST.get("price")

        product.sale_price = request.POST.get("sale_price") or None

        product.stock = request.POST.get("stock")

        product.material = request.POST.get("material")

        product.size = request.POST.get("size")

        product.color = request.POST.get("color")

        product.description = request.POST.get("description")

        # Product Flags

        product.is_new = True if request.POST.get("is_new") else False

        product.is_sale = True if request.POST.get("is_sale") else False

        product.is_featured = True if request.POST.get("is_featured") else False

        product.is_best_seller = True if request.POST.get("is_best_seller") else False

        if request.FILES.get("main_image"):

            product.main_image = request.FILES.get("main_image")

        product.save()

        return redirect("dashboard:products")

    return render(
        request,
        "dashboard/products/edit.html",
        {"product": product, "categories": categories, "subcategories": subcategories},
    )


# ============================
# PRODUCT DELETE
# ============================

@login_required
def product_delete(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":

        product.delete()

        return redirect("dashboard:products")

    return render(request, "dashboard/products/delete.html", {"product": product})


# ============================================
# CATEGORIES
# ============================================

@login_required
def category_list(request):

    categories = Category.objects.all()

    return render(request, "dashboard/categories/list.html", {"categories": categories})

@login_required
def category_add(request):

    if request.method == "POST":

        Category.objects.create(
            name=request.POST.get("name"),
            icon_class=request.POST.get("icon_class"),
            image=request.FILES.get("image"),
            is_active=True,
        )

        return redirect("dashboard:categories")

    return render(request, "dashboard/categories/add.html")

@login_required
def category_delete(request, id):

    category = get_object_or_404(Category, id=id)

    if request.method == "POST":

        category.delete()

        return redirect("dashboard:categories")

    return render(request, "dashboard/categories/delete.html", {"category": category})


# ============================================
# SUBCATEGORIES
# ============================================

@login_required
def subcategory_list(request):

    subcategories = SubCategory.objects.select_related("category").all()

    return render(
        request, "dashboard/subcategories/list.html", {"subcategories": subcategories}
    )

@login_required
def subcategory_add(request):

    categories = Category.objects.all()

    if request.method == "POST":

        SubCategory.objects.create(
            category_id=request.POST.get("category"),
            name=request.POST.get("name"),
            image=request.FILES.get("image"),
            is_active=True,
        )

        return redirect("dashboard:subcategories")

    return render(
        request, "dashboard/subcategories/add.html", {"categories": categories}
    )

@login_required
def subcategory_delete(request, id):

    subcategory = get_object_or_404(SubCategory, id=id)

    if request.method == "POST":

        subcategory.delete()

        return redirect("dashboard:subcategories")

    return render(
        request, "dashboard/subcategories/delete.html", {"subcategory": subcategory}
    )


# ============================
# LOAD SUBCATEGORIES AJAX
# ============================

@login_required
def load_subcategories(request):

    category_id = request.GET.get("category_id")

    subcategories = SubCategory.objects.filter(category_id=category_id, is_active=True)

    data = []

    for sub in subcategories:

        data.append({"id": sub.id, "name": sub.name})

    return JsonResponse({"subcategories": data})


# ============================================
# ORDERS
# ============================================

@login_required
def order_list(request):

    orders = Order.objects.all().order_by("-created_at")

    return render(request, "dashboard/orders/list.html", {"orders": orders})

@login_required
def order_detail(request, id):

    order = get_object_or_404(Order, id=id)

    return render(request, "dashboard/orders/detail.html", {"order": order})

@login_required
def order_invoice(request, id):

    order = get_object_or_404(Order, id=id)

    return render(request, "dashboard/orders/invoice.html", {"order": order})

@login_required
def update_order_status(request, id):

    order = get_object_or_404(Order, id=id)

    if request.method == "POST":

        order.status = request.POST.get("status")

        order.save()

        return redirect("dashboard:orders")

    return redirect("dashboard:orders")


# ============================
# INVENTORY MANAGEMENT
# ============================

@login_required
def dispatch_order(request, id):

    order = get_object_or_404(Order, id=id)

    if request.method == "POST":

        order.courier_name = request.POST.get("courier_name")

        order.tracking_number = request.POST.get("tracking_number")

        order.status = "Shipped"

        order.dispatch_date = timezone.now()

        order.save()

        return redirect("dashboard:order_detail", id=id)

    return redirect("dashboard:orders")

@login_required
def add_return(request, id):

    order = get_object_or_404(Order, id=id)

    if request.method == "POST":

        product_id = request.POST.get("product")

        quantity = int(request.POST.get("quantity"))

        reason = request.POST.get("reason")

        product = get_object_or_404(Product, id=product_id)

        ProductReturn.objects.create(
            order=order, product=product, quantity=quantity, reason=reason
        )

        # Stock wapas add

        product.stock += quantity

        product.save()

        InventoryHistory.objects.create(
            product=product, quantity=quantity, note="Customer Return"
        )

        return redirect("dashboard:order_detail", id=id)

    return redirect("dashboard:orders")


# ============================================
# STOCK / INVENTORY
# ============================================

@login_required
def stock_list(request):

    products = Product.objects.all().order_by("name")

    return render(request, "dashboard/stock/list.html", {"products": products})

@login_required
def stock_in(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":

        quantity = int(request.POST.get("quantity"))

        note = request.POST.get("note")

        product.stock += quantity

        product.save()

        InventoryHistory.objects.create(product=product, quantity=quantity, note=note)

        return redirect("dashboard:stock")

    return render(request, "dashboard/stock/in.html", {"product": product})

@login_required
def stock_out(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":

        quantity = int(request.POST.get("quantity"))

        note = request.POST.get("note")

        if product.stock >= quantity:

            product.stock -= quantity

            product.save()

            InventoryHistory.objects.create(
                product=product, quantity=-quantity, note=note
            )

        return redirect("dashboard:stock")

    return render(request, "dashboard/stock/out.html", {"product": product})

@login_required
def stock_history(request):

    history = InventoryHistory.objects.select_related("product").order_by("-id")

    return render(request, "dashboard/stock/history.html", {"history": history})

@login_required
def low_stock_list(request):

    products = Product.objects.filter(stock__lte=F("low_stock_limit")).order_by("stock")

    return render(request, "dashboard/stock/low_stock.html", {"products": products})


# ============================================
# CUSTOMERS
# ============================================

@login_required
def customer_list(request):

    customers = (
        Order.objects.values("full_name", "phone", "email")
        .annotate(
            total_orders=Count("id"),
            total_spent=Sum("total"),
            last_order=Max("created_at"),
        )
        .order_by("-last_order")
    )

    return render(request, "dashboard/customers/list.html", {"customers": customers})


# ============================================
# REPORTS
# ============================================

@login_required
def sales_report(request):

    today = timezone.now().date()

    today_sale = (
        Order.objects.filter(created_at__date=today, payment_status="Paid").aggregate(
            total=Sum("total")
        )["total"]
        or 0
    )

    month_sale = (
        Order.objects.filter(
            created_at__month=today.month,
            created_at__year=today.year,
            payment_status="Paid",
        ).aggregate(total=Sum("total"))["total"]
        or 0
    )

    total_sale = (
        Order.objects.filter(payment_status="Paid").aggregate(total=Sum("total"))[
            "total"
        ]
        or 0
    )

    pending_payment = (
        Order.objects.filter(payment_status="Pending").aggregate(total=Sum("total"))[
            "total"
        ]
        or 0
    )

    return render(
        request,
        "dashboard/reports/sales.html",
        {
            "today_sale": today_sale,
            "month_sale": month_sale,
            "total_sale": total_sale,
            "pending_payment": pending_payment,
        },
    )

@login_required
def product_report(request):

    products = (
        OrderItem.objects.values("product__name")
        .annotate(total_quantity=Sum("quantity"), total_sales=Sum("price"))
        .order_by("-total_quantity")
    )

    return render(request, "dashboard/reports/products.html", {"products": products})

@login_required
def payment_report(request):

    payments = (
        Order.objects.filter(payment_status="Paid")
        .values("payment_method")
        .annotate(total_amount=Sum("total"), total_orders=Count("id"))
        .order_by("-total_amount")
    )

    return render(request, "dashboard/reports/payment.html", {"payments": payments})


# ============================================
# ACCOUNT / PROFILE
# ============================================

@login_required
def account(request):

    if request.method == "POST":

        user = request.user
        new_username = request.POST.get("username")

        # Check karein ke ye username kisi AUR user ke pas to nahi
        username_taken = User.objects.filter(username=new_username).exclude(id=user.id).exists()

        if username_taken:

            messages.error(request, "Ye username pehle se kisi aur account mein use ho raha hai. Koi aur username chunein.")

            return redirect("dashboard:account")

        user.username = new_username
        user.email = request.POST.get("email")
        user.first_name = request.POST.get("first_name")

        user.save()

        messages.success(request, "Profile updated successfully")

        return redirect("dashboard:account")

    return render(request, "dashboard/account.html")

# ============================
# CHANGE PASSWORD
# ============================

@login_required
def change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(request, user)

            messages.success(request, "Password changed successfully")

            return redirect("dashboard:account")

    else:

        form = PasswordChangeForm(request.user)

    return render(request, "dashboard/change_password.html", {"form": form})


# ============================================
# BANNERS
# ============================================

@login_required
def banner_list(request):

    banners = Banner.objects.all()

    return render(
        request,
        "dashboard/banners/list.html",
        {
            "banners": banners
        }
    )

@login_required
def banner_add(request):

    if request.method == "POST":

        Banner.objects.create(

            title=request.POST.get("title"),

            description=request.POST.get("description"),

            image=request.FILES.get("image"),

            button_text=request.POST.get("button_text"),

            button_link=request.POST.get("button_link"),

            is_active=True

        )

        return redirect("dashboard:banners")


    return render(
        request,
        "dashboard/banners/add.html"
    )    
    
    
 # =====================================
# BANNER EDIT
# =====================================

@login_required
def banner_edit(request, id):

    banner = get_object_or_404(
        Banner,
        id=id
    )


    if request.method == "POST":

        banner.title = request.POST.get("title")
        banner.description = request.POST.get("description")
        banner.button_text = request.POST.get("button_text")
        banner.button_link = request.POST.get("button_link")
        banner.is_active = True


        if request.FILES.get("image"):
            banner.image = request.FILES.get("image")


        banner.save()


        return redirect(
            "dashboard:banners"
        )


    return render(
        request,
        "dashboard/banners/edit.html",
        {
            "banner": banner
        }
    )


# =====================================
# BANNER DELETE
# =====================================

@login_required
def banner_delete(request, id):

    banner = get_object_or_404(
        Banner,
        id=id
    )


    banner.delete()


    return redirect(
        "dashboard:banners"
    )   
    
    


# ============================================
# BEST SELLERS
# ============================================

@login_required
def best_seller_list(request):

    products = (
        OrderItem.objects
        .values("product__name")
        .annotate(
            total_quantity=Sum("quantity"),
            total_sales=Sum("price")
        )
        .order_by("-total_quantity")
    )


    return render(
        request,
        "dashboard/best_sellers/list.html",
        {
            "products": products
        }
    )    


# ============================================
# INSTAGRAM
# ============================================

@login_required
def instagram_list(request):

    posts = InstagramPost.objects.all().order_by("-id")

    return render(
        request,
        "dashboard/instagram/list.html",
        {
            "posts": posts
        }
    )      

@login_required
def instagram_add(request):

    if request.method == "POST":

        InstagramPost.objects.create(
            image=request.FILES.get("image"),
            caption=request.POST.get("caption"),
            link=request.POST.get("link"),
            is_active=True,
        )

        return redirect("dashboard:instagram")

    return render(request, "dashboard/instagram/add.html")

@login_required
def instagram_edit(request, id):

    post = get_object_or_404(InstagramPost, id=id)

    if request.method == "POST":

        post.caption = request.POST.get("caption")
        post.link = request.POST.get("link")

        if request.FILES.get("image"):
            post.image = request.FILES.get("image")

        post.save()

        return redirect("dashboard:instagram")

    return render(request, "dashboard/instagram/edit.html", {"post": post})

@login_required
def instagram_delete(request, id):

    post = get_object_or_404(InstagramPost, id=id)

    if request.method == "POST":
        post.delete()
        return redirect("dashboard:instagram")

    return render(request, "dashboard/instagram/delete.html", {"post": post})


# ============================================
# OFFERS
# ============================================

@login_required
def offer_list(request):

    offers = Offer.objects.all().order_by("-id")

    return render(
        request,
        "dashboard/offers/list.html",
        {
            "offers": offers
        }
    )


# =====================================
# ADD OFFER
# =====================================

@login_required
def offer_add(request):

    if request.method == "POST":

        Offer.objects.create(

            title=request.POST.get("title"),

            description=request.POST.get("description"),

            discount=request.POST.get("discount"),

            image=request.FILES.get("image"),

            active=True

        )


        return redirect(
            "dashboard:offers"
        )


    return render(
        request,
        "dashboard/offers/add.html"
    )


# =====================================
# EDIT OFFER
# =====================================

@login_required
def offer_edit(request, id):

    offer = get_object_or_404(
        Offer,
        id=id
    )


    if request.method == "POST":

        offer.title = request.POST.get("title")

        offer.description = request.POST.get("description")

        offer.discount = request.POST.get("discount")


        if request.FILES.get("image"):

            offer.image = request.FILES.get("image")


        offer.save()


        return redirect(
            "dashboard:offers"
        )


    return render(
        request,
        "dashboard/offers/edit.html",
        {
            "offer": offer
        }
    )


# =====================================
# DELETE OFFER
# =====================================

@login_required
def offer_delete(request, id):

    offer = get_object_or_404(
        Offer,
        id=id
    )


    offer.delete()


    return redirect(
        "dashboard:offers"
    )    


# ============================================
# SITE & STORE SETTINGS
# ============================================

@login_required
def store_setting(request):

    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to access this page.")
        return redirect("dashboard:home")

    setting = SiteSettings.objects.first()

    if not setting:
        setting = SiteSettings.objects.create()

    if request.method == "POST":

        setting.store_name = request.POST.get("store_name")
        setting.phone = request.POST.get("phone")
        setting.whatsapp = request.POST.get("whatsapp")
        setting.email = request.POST.get("email")
        setting.address = request.POST.get("address")
        setting.opening_hours = request.POST.get("opening_hours")
        setting.delivery_charges = request.POST.get("delivery_charges")

        if request.FILES.get("logo"):
            setting.logo = request.FILES.get("logo")

        setting.save()

        messages.success(request, "Store settings updated successfully")

        return redirect("dashboard:store_setting")

    return render(
        request,
        "dashboard/settings/store.html",
        {
            "setting": setting
        }
    )


@login_required
def site_setting(request):

    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to access this page.")
        return redirect("dashboard:home")

    setting = SiteSettings.objects.first()

    if not setting:
        setting = SiteSettings.objects.create()

    if request.method == "POST":

        setting.site_title = request.POST.get("site_title")
        setting.meta_description = request.POST.get("meta_description")
        setting.facebook = request.POST.get("facebook")
        setting.instagram = request.POST.get("instagram")
        setting.youtube = request.POST.get("youtube")
        setting.footer_text = request.POST.get("footer_text")
        setting.announcement_text = request.POST.get("announcement")

        if request.FILES.get("favicon"):
            setting.favicon = request.FILES.get("favicon")

        setting.save()

        messages.success(request, "Site settings updated successfully")

        return redirect("dashboard:site_setting")

    return render(
        request,
        "dashboard/settings/site.html",
        {
            "setting": setting
        }
    )