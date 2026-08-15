from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/add/<slug:slug>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("cart/increase/<int:item_id>/", views.increase_cart, name="increase_cart"),
    path("cart/decrease/<int:item_id>/", views.decrease_cart, name="decrease_cart"),
    path("cart/remove/<int:item_id>/", views.remove_cart, name="remove_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("order-success/", views.order_success, name="order_success"),
    path("search/", views.search, name="search"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.user_login, name="login"),
    path("signup/", views.user_signup, name="signup"),
    path("logout/", views.user_logout, name="logout"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/add/<slug:slug>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("wishlist/remove/<int:item_id>/", views.remove_wishlist, name="remove_wishlist"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("profile/", views.profile, name="profile"),
    path("my-orders/<int:order_id>/",views.order_detail,name="order_detail"),
]
