from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="subcategories"
    )

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True, null=True)

    image = models.ImageField(upload_to="subcategories/", blank=True, null=True)

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        unique_together = ("category", "name")

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Product(models.Model):

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )

    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.PROTECT, related_name="products"
    )

    name = models.CharField(max_length=200)

    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True)

    sku = models.CharField(max_length=100, unique=True)

    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=12, decimal_places=2)

    sale_price = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )

    stock = models.PositiveIntegerField(default=0)

    pieces = models.PositiveIntegerField(blank=True, null=True)

    material = models.CharField(max_length=100, blank=True)

    size = models.CharField(max_length=100, blank=True)

    color = models.CharField(max_length=100, blank=True)

    main_image = models.ImageField(upload_to="products/", blank=True, null=True)

    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)

    reviews = models.PositiveIntegerField(default=0)

    is_new = models.BooleanField(default=False)

    is_sale = models.BooleanField(default=False)

    is_featured = models.BooleanField(default=False)

    is_best_seller = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("store:product_detail", kwargs={"slug": self.slug})

    @property
    def final_price(self):
        if self.sale_price:
            return self.sale_price
        return self.price

    @property
    def in_stock(self):
        return self.stock > 0


class Cart(models.Model):

    session_key = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.session_key


class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    @property
    def subtotal(self):
        return self.product.final_price * self.quantity

    def __str__(self):
        return self.product.name


class ProductImage(models.Model):

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )

    image = models.ImageField(upload_to="products/gallery/")

    is_main = models.BooleanField(default=False)

    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.product.name} Image"


class Banner(models.Model):

    title = models.CharField(max_length=200, blank=True)

    subtitle = models.CharField(max_length=300, blank=True)

    image = models.ImageField(upload_to="banners/")

    button_text = models.CharField(max_length=50, blank=True)

    button_url = models.CharField(max_length=300, blank=True)

    is_active = models.BooleanField(default=True)

    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.title or "Banner"


class Offer(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    image = models.ImageField(upload_to="offers/", blank=True, null=True)

    discount_text = models.CharField(max_length=100, blank=True)

    is_active = models.BooleanField(default=True)

    start_date = models.DateField(blank=True, null=True)

    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title


class SiteSettings(models.Model):

    store_name = models.CharField(max_length=150, default="Maryam Crockery")

    logo = models.ImageField(upload_to="site/", blank=True, null=True)

    tagline = models.CharField(max_length=200, blank=True)

    phone = models.CharField(max_length=30, blank=True)

    email = models.EmailField(blank=True)

    address = models.TextField(blank=True)

    facebook = models.URLField(blank=True)

    instagram = models.URLField(blank=True)

    youtube = models.URLField(blank=True)

    whatsapp = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.store_name


# ======================================
# Order
# ======================================


class Order(models.Model):

    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    )

    PAYMENT_CHOICES = (
        ("COD", "Cash On Delivery"),
        ("JazzCash", "JazzCash"),
        ("EasyPaisa", "EasyPaisa"),
        ("Bank", "Bank Transfer"),
    )

    order_number = models.CharField(max_length=30, unique=True)

    full_name = models.CharField(max_length=200)

    phone = models.CharField(max_length=20)

    email = models.EmailField(blank=True)

    address = models.TextField()

    city = models.CharField(max_length=120)

    notes = models.TextField(blank=True)

    payment_method = models.CharField(
        max_length=30, choices=PAYMENT_CHOICES, default="COD"
    )

    total = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_number


# ======================================
# Order Item
# ======================================


class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )

    price = models.DecimalField(max_digits=12, decimal_places=2)

    quantity = models.PositiveIntegerField()

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        if self.product:
            return f"{self.order.order_number} - {self.product.name}"
        return f"{self.order.order_number} - Deleted Product"

    # ==========================================


# AUTO GENERATE SLUG
# ==========================================


@receiver(pre_save, sender=Category)
def category_slug(sender, instance, **kwargs):

    if not instance.slug:
        instance.slug = slugify(instance.name)


@receiver(pre_save, sender=SubCategory)
def subcategory_slug(sender, instance, **kwargs):

    if not instance.slug:
        instance.slug = slugify(instance.name)


@receiver(pre_save, sender=Product)
def product_slug(sender, instance, **kwargs):

    if not instance.slug:
        instance.slug = slugify(instance.name)
