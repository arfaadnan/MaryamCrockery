from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.db import models

# ======================================
# Category & SubCategory Models
# ======================================


class Category(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True, default="", blank=True)
    icon_class = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. bi-cup-hot, bi-bag")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="subcategories"
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True, null=True, db_index=True)
    image = models.ImageField(upload_to="subcategories/", blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        unique_together = ("category", "name")

    def __str__(self):
        return f"{self.category.name} - {self.name}"


# ======================================
# Product Model
# ======================================


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.PROTECT, related_name="products", blank=True, null=True
    )
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True, db_index=True)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    sale_price = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True, db_index=True
    )
    discount_price = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    
    stock = models.PositiveIntegerField(default=0)
    low_stock_limit = models.PositiveIntegerField(default=5)
    pieces = models.PositiveIntegerField(blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, db_index=True)
    size = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=100, blank=True)
    
    main_image = models.ImageField(upload_to="products/", blank=True, null=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    reviews = models.PositiveIntegerField(default=0)
    
    is_new = models.BooleanField(default=False)
    is_sale = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
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
        effective_sale = self.sale_price or self.discount_price
        if effective_sale and effective_sale < self.price:
            return effective_sale
        return self.price

    @property
    def discount_percentage(self):
        effective_sale = self.sale_price or self.discount_price
        if effective_sale and effective_sale < self.price:
            discount = ((self.price - effective_sale) / self.price) * 100
            return round(discount)
        return 0

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def low_stock(self):
        return self.stock <= self.low_stock_limit


# ======================================
# Product Gallery & Banner/Offer
# ======================================


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
    phone_number = models.CharField(max_length=20, default="+92 322 3489220")
    whatsapp = models.CharField(max_length=30, blank=True)
    whatsapp_number = models.CharField(max_length=20, default="923223489220")
    bank_name = models.CharField(max_length=100, blank=True, default="")
    bank_account_title = models.CharField(max_length=150, blank=True, default="")
    bank_account_number = models.CharField(max_length=50, blank=True, default="")
    bank_iban = models.CharField(max_length=50, blank=True, default="")
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    announcement_text = models.CharField(max_length=255, default="Fast Delivery All Across Pakistan!")
    is_announcement_active = models.BooleanField(default=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)

    def __str__(self):
        return self.store_name


# ======================================
# Cart & Cart Items
# ======================================


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=100, unique=True, db_index=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.session_key or f"User Cart ({self.user.username if self.user else 'Guest'})"

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


# ======================================
# Order & Order Items
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

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=30, unique=True, db_index=True)
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
    PAYMENT_STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Failed", "Failed"),
    )

    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="Pending", db_index=True
    )
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_response = models.TextField(blank=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    payment_proof = models.ImageField(upload_to="payment_proofs/", blank=True, null=True)

    courier_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    dispatch_date = models.DateTimeField(
        blank=True,
        null=True
    )
    def __str__(self):
        return self.order_number


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


# ======================================
# Wishlist & Wishlist Items
# ======================================


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, unique=True, db_index=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.session_key or f"User Wishlist ({self.user.username if self.user else 'Guest'})"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("wishlist", "product")

    def __str__(self):
        return self.product.name


# ======================================
# User Profile
# ======================================


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


# ======================================
# Product Reviews
# ======================================


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.user.username}"


# ======================================
# Inventory History
# ======================================


class InventoryHistory(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory_history",
    )
    quantity = models.IntegerField()
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


# ======================================
# Signals (Slug Generation & Profile Auto-Creation)
# ======================================


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


@receiver(post_save, sender=User)
def create_or_save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
        instance.profile.save()
        
        ########invoice
        
class StoreSetting(models.Model):
    store_name = models.CharField(max_length=150, default="My E-Commerce Store")
    tagline = models.CharField(max_length=200, blank=True, default="Quality Products at Your Doorstep")
    phone = models.CharField(max_length=20, default="0300-1234567")
    email = models.EmailField(default="support@store.com")
    address = models.TextField(default="Karachi, Pakistan")
    
    # Bank Details for Invoice
    bank_name = models.CharField(max_length=100, blank=True)
    account_title = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=100, blank=True)
    
    # Footer Note
    invoice_footer = models.TextField(default="Thank you for shopping with us! No return after 7 days.")

    def save(self, *args, **kwargs):
        # Yeh ensure karta hai ke database mein sirf ek hi settings row rahe
        self.pk = 1
        super(StoreSetting, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Store & Invoice Settings"        
    
# ======================================
# Product Return Management
# ======================================

class ProductReturn(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="returns"
    )


    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )


    quantity = models.PositiveIntegerField()


    reason = models.TextField(
        blank=True
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):

        return f"{self.order.order_number} - {self.product.name}"