from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "store"

urlpatterns = [
    # Pages & Core Navigation
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("category/<slug:slug>/", views.category_products, name="category_products"),
    path(
        "subcategory/<slug:slug>/",
        views.subcategory_products,
        name="subcategory_products",
    ),
    # Cart & Checkout Routes
    path("cart/", views.cart, name="cart"),
    path("cart/add/<slug:slug>/", views.add_to_cart, name="add_to_cart"),
    path("buy-now/<slug:slug>/", views.buy_now, name="buy_now"),
    path("cart/increase/<int:item_id>/", views.increase_cart, name="increase_cart"),
    path("cart/decrease/<int:item_id>/", views.decrease_cart, name="decrease_cart"),
    path("cart/remove/<int:item_id>/", views.remove_cart, name="remove_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("order-success/<int:order_id>/", views.order_success, name="order_success"),
    # Search & Filters
    path("search/", views.search, name="search"),
    # -----------------------------------------------------------------
    # Naye Naheed-Style Endpoints (AJAX & Fast Interactivity)
    # -----------------------------------------------------------------
    path(
        "ajax/live-search/", views.live_search, name="live_search"
    ),  # Typing par instant visual results
    path(
        "ajax/cart/add/", views.ajax_add_to_cart, name="ajax_add_to_cart"
    ),  # Bina page reload kiye cart update
    path(
        "ajax/cart/drawer/", views.get_cart_drawer, name="get_cart_drawer"
    ),  # Off-canvas side drawer loader
    # -----------------------------------------------------------------
    # User Accounts & Profiles
    path("login/", views.user_login, name="login"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="store/password_reset.html",
            email_template_name="store/password_reset_email.html",
            subject_template_name="store/password_reset_subject.txt",
            success_url="/password-reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="store/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="store/password_reset_confirm.html",
            success_url="/reset/done/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="store/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("signup/", views.user_signup, name="signup"),
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("my-orders/<int:order_id>/", views.order_detail, name="order_detail"),
    # Wishlist
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/add/<slug:slug>/", views.add_to_wishlist, name="add_to_wishlist"),
    path(
        "wishlist/remove/<int:item_id>/", views.remove_wishlist, name="remove_wishlist"
    ),
    # Reviews & Feedback
    path("review/<slug:slug>/", views.add_review, name="add_review"),
    # Admin & Information Pages
    path("contact/", views.contact, name="contact"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("terms-conditions/", views.terms_conditions, name="terms_conditions"),
    path("refund-policy/", views.refund_policy, name="refund_policy"),
    path("inventory/low-stock/", views.low_stock_products, name="low_stock_products"),
    path(
        "ajax/load-subcategories/", views.load_subcategories, name="load_subcategories"
    ),
    path(
        "payment/jazzcash/start/<int:order_id>/",
        views.start_jazzcash_payment,
        name="jazzcash_start",
    ),
    path(
        "payment/jazzcash/callback/", views.jazzcash_callback, name="jazzcash_callback"
    ),
    path(
        "payment/easypaisa/start/<int:order_id>/",
        views.start_easypaisa_payment,
        name="easypaisa_start",
    ),
    path(
        "payment/easypaisa/callback/",
        views.easypaisa_callback,
        name="easypaisa_callback",
    ),
]
