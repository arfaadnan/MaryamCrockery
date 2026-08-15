from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path("product/<slug:slug>/",views.product_detail,name="product_detail"),
    path("cart/add/<slug:slug>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("cart/increase/<int:item_id>/",views.increase_cart,name="increase_cart"),
    path("cart/decrease/<int:item_id>/",views.decrease_cart,name="decrease_cart"),
    path("cart/remove/<int:item_id>/",views.remove_cart,name="remove_cart"),
]