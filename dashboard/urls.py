from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [

    # ============================
    # AUTH
    # ============================
    path("login/", views.manager_login, name="login"),
    path("logout/", views.manager_logout, name="logout"),
    path("", views.dashboard_home, name="home"),

    # ============================
    # PRODUCT URLS
    # ============================
    path("products/", views.product_list, name="products"),
    path("products/add/", views.product_add, name="product_add"),
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
    # ORDER URLS
    # ============================
    path("orders/", views.order_list, name="orders"),
    path("orders/<int:id>/", views.order_detail, name="order_detail"),
    path("orders/update/<int:id>/", views.update_order_status, name="update_order_status"),
    path("orders/dispatch/<int:id>/", views.dispatch_order, name="dispatch_order"),
    path("orders/return/<int:id>/", views.add_return, name="add_return"),
    path("orders/invoice/<int:id>/", views.order_invoice, name="order_invoice"),

    # ============================
    # STOCK URLS
    # ============================
    path("stock/", views.stock_list, name="stock"),
    path("stock/in/<int:id>/", views.stock_in, name="stock_in"),
    path("stock/out/<int:id>/", views.stock_out, name="stock_out"),
    path("stock/history/", views.stock_history, name="stock_history"),
    path("stock/low/", views.low_stock_list, name="low_stock"),

    # ============================
    # CUSTOMERS
    # ============================
    path("customers/", views.customer_list, name="customers"),

    # ============================
    # REPORTS
    # ============================
    path("reports/sales/", views.sales_report, name="sales_report"),
    path("reports/products/", views.product_report, name="product_report"),
    path("reports/payment/", views.payment_report, name="payment_report"),

    # ============================
    # ACCOUNT
    # ============================
    path("account/", views.account, name="account"),
    path("account/change-password/", views.change_password, name="change_password"),

    # =====================================
    # BANNER CRUD URLS
    # =====================================
    path("banners/", views.banner_list, name="banners"),
    path("banners/add/", views.banner_add, name="banner_add"),
    path("banners/edit/<int:id>/", views.banner_edit, name="banner_edit"),
    path("banners/delete/<int:id>/", views.banner_delete, name="banner_delete"),

    # ============================
    # BEST SELLERS
    # ============================
    path("best-sellers/", views.best_seller_list, name="best_sellers"),

    # ============================
    # INSTAGRAM
    # ============================
    path("instagram/", views.instagram_list, name="instagram"),
    path("instagram/add/", views.instagram_add, name="instagram_add"),
    path("instagram/edit/<int:id>/", views.instagram_edit, name="instagram_edit"),
    path("instagram/delete/<int:id>/", views.instagram_delete, name="instagram_delete"),

    # =====================================
    # OFFER URLS
    # =====================================
    path("offers/", views.offer_list, name="offers"),
    path("offers/add/", views.offer_add, name="offer_add"),
    path("offers/edit/<int:id>/", views.offer_edit, name="offer_edit"),
    path("offers/delete/<int:id>/", views.offer_delete, name="offer_delete"),

    # ============================
    # SETTINGS
    # ============================
    path("settings/store/", views.store_setting, name="store_setting"),
    path("settings/site/", views.site_setting, name="site_setting"),

]