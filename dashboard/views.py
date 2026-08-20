from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.db.models import Count, Sum, Max

from store.models import Product, Order, OrderItem

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


from django.shortcuts import render, redirect, get_object_or_404

from store.models import Product, InventoryHistory


from store.models import Product, Category, SubCategory, ProductImage


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from store.models import Category, SubCategory

from django.http import JsonResponse


from django.db import transaction
from store.models import Order
from django.utils import timezone
from store.models import ProductReturn

# ============================
# ORDER IMPORTS
# ============================

from store.models import Order

# ============================
# DASHBOARD IMPORTS
# ============================

from django.db.models import Sum
from django.utils import timezone

from store.models import Product, Order

from django.db.models import Sum, F
from django.utils import timezone


@login_required
def dashboard_home(request):

    # Dashboard Statistics

    total_products = Product.objects.count()

    total_orders = Order.objects.count()
    
    total_categories = Category.objects.count()

    # Today's Sale

    today = timezone.now().date()

    today_sale = (
        Order.objects.filter(
            created_at__date=today,
            payment_status="Paid"
        )
        .aggregate(
            total=Sum("total")
        )["total"]
        or 0
    )


    # Total Sale

    total_sale = (
        Order.objects.filter(
            payment_status="Paid"
        )
        .aggregate(
            total=Sum("total")
        )["total"]
        or 0
    )


    # Pending Payment

    pending_payment = (
        Order.objects.filter(
            payment_status="Pending"
        )
        .aggregate(
            total=Sum("total")
        )["total"]
        or 0
    )


    # Paid Orders Count

    paid_orders = Order.objects.filter(
        payment_status="Paid"
    ).count()



    # Order Status Count

    pending_orders = Order.objects.filter(
        status="Pending"
    ).count()


    confirmed_orders = Order.objects.filter(
        status="Confirmed"
    ).count()


    shipped_orders = Order.objects.filter(
        status="Shipped"
    ).count()


    delivered_orders = Order.objects.filter(
        status="Delivered"
    ).count()



    # Low Stock Count

    low_stock = Product.objects.filter(
        stock__lte=F("low_stock_limit")
    ).count()



    # Recent Orders

    recent_orders = Order.objects.all().order_by(
        "-created_at"
    )[:5]



    # Low Stock Products

    low_stock_products = Product.objects.filter(
        stock__lte=F("low_stock_limit")
    )[:5]



    # Material Wise Stock

    material_stock = (
        Product.objects.values("material")
        .annotate(
            total_products=Count("id"),
            total_stock=Sum("stock")
        )
        .order_by("-total_stock")
    )



    # Cash Report

    now = timezone.now()


    month_sale = (
        Order.objects.filter(
            created_at__year=now.year,
            created_at__month=now.month,
            payment_status="Paid"
        )
        .aggregate(
            total=Sum("total")
        )["total"]
        or 0
    )



    cod_sale = (
        Order.objects.filter(
            payment_method="COD",
            payment_status="Paid"
        )
        .aggregate(
            total=Sum("total")
        )["total"]
        or 0
    )



    online_sale = (
        Order.objects.filter(
            payment_method__in=[
                "JazzCash",
                "EasyPaisa",
                "Bank"
            ],
            payment_status="Paid"
        )
        .aggregate(
            total=Sum("total")
        )["total"]
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


    return render(
        request,
        "dashboard/dashboard.html",
        context
    )    
    

    # ============================
    # CASH REPORT
    # ============================

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
        "today_sale": today_sale,
        "total_sale": total_sale,
        "pending_payment": pending_payment,
        "paid_orders": paid_orders,
        "low_stock": low_stock,
        "recent_orders": recent_orders,
        "low_stock_products": low_stock_products,
        "material_stock": material_stock,
        "month_sale": month_sale,
        "cod_sale": cod_sale,
        "online_sale": online_sale,
    }

    return render(request, "dashboard/dashboard.html", context)


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


# ============================
# PRODUCT MANAGEMENT
# ============================


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

            ProductImage.objects.create(

                product=product,

                image=image

            )

        return redirect("dashboard:products")

    return render(
        request,
        "dashboard/products/add.html",
        {
            "categories": categories
        }
    )

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


# ============================
# CATEGORY MANAGEMENT
# ============================


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


# ============================
# SUBCATEGORY MANAGEMENT
# ============================


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


# ============================
# ORDER MANAGEMENT
# ============================


@login_required
def order_list(request):

    orders = Order.objects.all().order_by("-created_at")

    return render(request, "dashboard/orders/list.html", {"orders": orders})

@login_required
def customer_list(request):

    customers = (
        Order.objects
        .values(
            "full_name",
            "phone",
            "email"
        )
        .annotate(
            total_orders=Count("id"),
            total_spent=Sum("total"),
            last_order=Max("created_at")
        )
        .order_by("-last_order")
    )


    return render(
        request,
        "dashboard/customers/list.html",
        {
            "customers": customers
        }
    )


@login_required
def sales_report(request):

    today = timezone.now().date()


    today_sale = (
        Order.objects.filter(
            created_at__date=today,
            payment_status="Paid"
        )
        .aggregate(
            total=Sum("total")
        )["total"] or 0
    )


    month_sale = (
        Order.objects.filter(
            created_at__month=today.month,
            created_at__year=today.year,
            payment_status="Paid"
        )
        .aggregate(
            total=Sum("total")
        )["total"] or 0
    )


    total_sale = (
        Order.objects.filter(
            payment_status="Paid"
        )
        .aggregate(
            total=Sum("total")
        )["total"] or 0
    )


    pending_payment = (
        Order.objects.filter(
            payment_status="Pending"
        )
        .aggregate(
            total=Sum("total")
        )["total"] or 0
    )


    return render(
        request,
        "dashboard/reports/sales.html",
        {
            "today_sale": today_sale,
            "month_sale": month_sale,
            "total_sale": total_sale,
            "pending_payment": pending_payment,
        }
    )

@login_required
def product_report(request):

    products = (
        OrderItem.objects
        .values(
            "product__name"
        )
        .annotate(
            total_quantity=Sum("quantity"),
            total_sales=Sum("price")
        )
        .order_by(
            "-total_quantity"
        )
    )


    return render(
        request,
        "dashboard/reports/products.html",
        {
            "products": products
        }
    )

@login_required
def payment_report(request):

    payments = (
        Order.objects
        .filter(payment_status="Paid")
        .values("payment_method")
        .annotate(
            total_amount=Sum("total"),
            total_orders=Count("id")
        )
        .order_by("-total_amount")
    )


    return render(
        request,
        "dashboard/reports/payment.html",
        {
            "payments": payments
        }
    )

pending_orders = Order.objects.filter(
    status="Pending"
).count()


confirmed_orders = Order.objects.filter(
    status="Confirmed"
).count()


shipped_orders = Order.objects.filter(
    status="Shipped"
).count()


delivered_orders = Order.objects.filter(
    status="Delivered"
).count()

@login_required
def order_detail(request, id):

    order = get_object_or_404(Order, id=id)

    return render(request, "dashboard/orders/detail.html", {"order": order})

@login_required
def order_invoice(request, id):

    order = get_object_or_404(
        Order,
        id=id
    )


    return render(
        request,
        "dashboard/orders/invoice.html",
        {
            "order": order
        }
    )
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

                product=product,

                quantity=-quantity,

                note=note

            )


        return redirect("dashboard:stock")


    return render(
        request,
        "dashboard/stock/out.html",
        {
            "product": product
        }
    )



@login_required
def stock_history(request):

    history = (
        InventoryHistory.objects
        .select_related("product")
        .order_by("-id")
    )

    return render(
        request,
        "dashboard/stock/history.html",
        {
            "history": history
        }
    )
    
@login_required
def low_stock_list(request):

    products = Product.objects.filter(
        stock__lte=F("low_stock_limit")
    ).order_by("stock")


    return render(
        request,
        "dashboard/stock/low_stock.html",
        {
            "products": products
        }
    )
    
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
