from django.db import models


# from products.models import Product



# =====================================
# BANNER MODEL
# =====================================

class Banner(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="banners/"
    )

    button_text = models.CharField(
        max_length=50,
        default="Shop Now"
    )

    button_link = models.CharField(
        max_length=200,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.title




# =====================================
# INSTAGRAM POST MODEL
# =====================================

class InstagramPost(models.Model):

    image = models.ImageField(
        upload_to="instagram/"
    )

    caption = models.TextField(
        blank=True
    )

    link = models.URLField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )


    def __str__(self):
        return self.caption[:30]




# =====================================
# OFFER MODEL
# =====================================

class Offer(models.Model):

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    discount = models.CharField(
        max_length=50
    )

    image = models.ImageField(
        upload_to="offers/",
        blank=True,
        null=True
    )

    active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.title




# =====================================
# STORE SETTING MODEL
# =====================================

class StoreSetting(models.Model):

    store_name = models.CharField(
        max_length=200
    )

    logo = models.ImageField(
        upload_to="store/",
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=50,
        blank=True
    )

    whatsapp = models.CharField(
        max_length=50,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    opening_hours = models.CharField(
        max_length=200,
        blank=True
    )

    delivery_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )


    def __str__(self):
        return self.store_name




# =====================================
# SITE SETTING MODEL
# =====================================

class SiteSetting(models.Model):

    site_title = models.CharField(
        max_length=200
    )

    meta_description = models.TextField(
        blank=True
    )

    favicon = models.ImageField(
        upload_to="site/",
        blank=True,
        null=True
    )

    facebook = models.URLField(
        blank=True
    )

    instagram = models.URLField(
        blank=True
    )

    youtube = models.URLField(
        blank=True
    )

    footer_text = models.TextField(
        blank=True
    )

    announcement = models.CharField(
        max_length=300,
        blank=True
    )


    def __str__(self):
        return self.site_title




# # =====================================
# # ORDER ITEM MODEL
# # =====================================

# class OrderItem(models.Model):

#     order = models.ForeignKey(
#         Order,
#         on_delete=models.CASCADE,
#         related_name="items"
#     )


#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE
#     )


#     quantity = models.PositiveIntegerField(
#         default=1
#     )


#     price = models.DecimalField(
#         max_digits=10,
#         decimal_places=2
#     )


#     created_at = models.DateTimeField(
#         auto_now_add=True
#     )


#     def __str__(self):

#         return self.product.name