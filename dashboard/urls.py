from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("login/", views.manager_login, name="login"),
    path("logout/", views.manager_logout, name="logout"),
    path("", views.dashboard_home, name="home"),
    
    path("products/edit/<int:id>/", views.product_edit, name="product_edit"),
    path("products/delete/<int:id>/", views.product_delete, name="product_delete"),
    # ============================
    # CATEGORY URLS
    # ============================
    path("categories/", views.category_list, name="categories"),
    path("categories/add/", views.category_add, name="category_add"),
    path("categories/delete/<int:id>/", views.category_delete, name="category_delete"),
    # ============================
    # SUBCATEGORY URLS
    # ============================
    path("subcategories/", views.subcategory_list, name="subcategories"),
    path("subcategories/add/", views.subcategory_add, name="subcategory_add"),
    path(
        "subcategories/delete/<int:id>/",
        views.subcategory_delete,
        name="subcategory_delete",
    ),
    path(
        "ajax/load-subcategories/", views.load_subcategories, name="load_subcategories"
    ),
    
   # ============================
# PRODUCT URLS
# ============================

path(
    "products/",
    views.product_list,
    name="products"
),

path(
    "products/edit/<int:id>/",
    views.product_edit,
    name="product_edit"
),

path(
    "products/delete/<int:id>/",
    views.product_delete,
    name="product_delete"
),
path(
    "products/add/",
    views.product_add,
    name="product_add"
),

# ============================
# ORDER URLS
# ============================


path(
    "orders/",
    views.order_list,
    name="orders"
),


path(
    "orders/<int:id>/",
    views.order_detail,
    name="order_detail"
),


path(
    "orders/update/<int:id>/",
    views.update_order_status,
    name="update_order_status"
),

# ============================
# STOCK URLS
# ============================


path(
    "stock/",
    views.stock_list,
    name="stock"
),


path(
    "stock/in/<int:id>/",
    views.stock_in,
    name="stock_in"
),

path(
    "orders/dispatch/<int:id>/",
    views.dispatch_order,
    name="dispatch_order"
),

path(
    "orders/return/<int:id>/",
    views.add_return,
    name="add_return"
),
path(
    "stock/history/",
    views.stock_history,
    name="stock_history",
),
path(
    "stock/low/",
    views.low_stock_list,
    name="low_stock"
),
path(
    "stock/out/<int:id>/",
    views.stock_out,
    name="stock_out"
),
path(
    "orders/invoice/<int:id>/",
    views.order_invoice,
    name="order_invoice"
),

path(
    "customers/",
    views.customer_list,
    name="customers"
),

path(
    "reports/sales/",
    views.sales_report,
    name="sales_report"
),

path(
    "reports/products/",
    views.product_report,
    name="product_report"
),

path(
    "reports/payment/",
    views.payment_report,
    name="payment_report"
),
]
