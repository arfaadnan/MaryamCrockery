from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Banner,
    Category,
    InventoryHistory,
    Offer,
    Product,
    ProductImage,
    Review,
    SiteSettings,
    SubCategory,
    Order,
    OrderItem,
    StoreSetting,
    
)

   
# ==========================
# Category
# ==========================


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "name",
        "is_active",
        "sort_order",
    )

    list_editable = (
        "is_active",
        "sort_order",
    )

    search_fields = ("name",)

    ordering = (
        "sort_order",
        "name",
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="55" height="55" style="border-radius:8px;">',
                obj.image.url,
            )
        return "-"

    image_preview.short_description = "Image"


# ==========================
# SubCategory
# ==========================


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "is_active",
        "sort_order",
    )

    list_filter = (
        "category",
        "is_active",
    )

    list_editable = (
        "is_active",
        "sort_order",
    )

    search_fields = (
        "name",
        "category__name",
    )


# ==========================
# Product Images Inline
# ==========================


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # Form par ek waqt mein 3 extra image upload slots dikhenge


# ==========================
# Product Admin Form
# ==========================


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1. Agar purana product edit ho raha hai
        if self.instance and self.instance.pk and self.instance.category:
            self.fields["subcategory"].queryset = SubCategory.objects.filter(
                category=self.instance.category
            )

        # 2. Agar form submit hone ke baad validation error aaye
        elif "category" in self.data:
            try:
                category_id = int(self.data.get("category"))
                self.fields["subcategory"].queryset = SubCategory.objects.filter(
                    category_id=category_id
                )
            except (ValueError, TypeError):
                self.fields["subcategory"].queryset = SubCategory.objects.none()

        # 3. Naya product banate waqt safe fallback
        else:
            self.fields["subcategory"].queryset = SubCategory.objects.all()


# ==========================
# Product Admin Register
# ==========================


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm

    inlines = [
        ProductImageInline,
    ]

    prepopulated_fields = {
        "slug": ("name",),
    }

    list_display = (
        "image_preview",
        "name",
        "category",
        "subcategory",
        "price",
        "sale_price",
        "stock",
        "low_stock_limit",
        "stock_status",
        "is_featured",
        "is_best_seller",
        "is_active",
    )

    list_editable = (
        "price",
        "sale_price",
        "stock",
        "is_featured",
        "is_best_seller",
        "is_active",
    )

    list_filter = (
        "category",
        "subcategory",
        "is_featured",
        "is_best_seller",
        "is_sale",
        "is_new",
        "is_active",
    )

    search_fields = (
        "name",
        "sku",
        "slug",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "category",
                    "subcategory",
                    "name",
                    "slug",
                    "sku",
                    "description",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price",
                    "sale_price",
                )
            },
        ),
        (
            "Inventory",
            {
                "fields": (
                    "stock",
                    "pieces",
                )
            },
        ),
        (
            "Details",
            {
                "fields": (
                    "material",
                    "size",
                    "color",
                )
            },
        ),
        ("Image", {"fields": ("main_image",)}),
        (
            "Flags",
            {
                "fields": (
                    "is_new",
                    "is_sale",
                    "is_featured",
                    "is_best_seller",
                    "is_active",
                )
            },
        ),
        (
            "Ratings",
            {
                "fields": (
                    "rating",
                    "reviews",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    actions = ["restock_products"]

    def image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius:8px;">',
                obj.main_image.url,
            )
        return "-"

    image_preview.short_description = "Image"

    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html(
                '<span style="color:red;font-weight:bold;">Out of Stock</span>'
            )
        elif obj.stock <= 5:
            return format_html(
                '<span style="color:orange;font-weight:bold;">Low Stock ({})</span>',
                obj.stock,
            )
        return format_html(
            '<span style="color:green;font-weight:bold;">In Stock ({})</span>',
            obj.stock,
        )

    stock_status.short_description = "Inventory"

    def low_stock(self, obj):
        return getattr(obj, "low_stock", False)

    low_stock.boolean = True
    low_stock.short_description = "Low Stock"

    @admin.action(description="Add 10 Stock")
    def restock_products(self, request, queryset):
        for product in queryset:
            product.stock += 10
            product.save()

            InventoryHistory.objects.create(
                product=product,
                quantity=10,
                note="Admin Restock",
            )

        self.message_user(
            request,
            "10 stock added successfully.",
        )


# ==========================
# Banner
# ==========================


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_active",
        "sort_order",
    )

    list_editable = (
        "is_active",
        "sort_order",
    )


# ==========================
# Offer
# ==========================


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "discount_text",
        "is_active",
    )

    list_editable = ("is_active",)


# ==========================
# Site Settings
# ==========================


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "store_name",
        "phone",
        "email",
    )


# ==========================
# Review
# ==========================


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "rating",
        "is_approved",
        "created_at",
    )

    list_filter = (
        "is_approved",
        "rating",
    )

    search_fields = (
        "product__name",
        "user__username",
    )

    list_editable = ("is_approved",)

    actions = ["approve_reviews", "unapprove_reviews"]

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Unapprove selected reviews")
    def unapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)


# ==========================
# Inventory History
# ==========================


@admin.register(InventoryHistory)
class InventoryHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "quantity",
        "note",
        "created_at",
    )

    list_filter = ("created_at",)

    search_fields = (
        "product__name",
        "note",
    )

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)
    
    ###order order item
 
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # Ye fields Order ke andar table ki shakal mein show hongi
    readonly_fields = ('product', 'price', 'quantity', 'subtotal')
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Aapke models ki exact fields yahan use ki gayi hain
    list_display = ('order_number', 'full_name', 'phone', 'city', 'payment_method', 'payment_status', 'view_proof', 'total', 'status', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'city', 'created_at')
    search_fields = ('order_number', 'full_name', 'phone', 'email', 'transaction_id')
    inlines = [OrderItemInline]

    list_editable = ('status',)

    def view_proof(self, obj):
        if obj.payment_proof:
            return format_html('<a href="{}" target="_blank">Receipt Dekhein</a>', obj.payment_proof.url)
        return "—"
    view_proof.short_description = "Payment Proof"
    #####3invoice
@admin.register(StoreSetting)
class StoreSettingAdmin(admin.ModelAdmin):
    # Sirf edit karne ki ijazat ho, naya object create na ho sake
    def has_add_permission(self, request):
        return not StoreSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
    