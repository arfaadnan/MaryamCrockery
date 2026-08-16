from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Category,
    SubCategory,
    Product,
    ProductImage,
    Banner,
    Offer,
    SiteSettings,
    Review,
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


def stock_status(self, obj):

    if obj.stock == 0:
        return format_html(
            '<span style="color:red;font-weight:bold;">Out of Stock</span>'
        )

    elif obj.low_stock:
        return format_html(
            '<span style="color:orange;font-weight:bold;">Low Stock ({})</span>',
            obj.stock,
        )

    return format_html(
        '<span style="color:green;font-weight:bold;">In Stock ({})</span>',
        obj.stock,
    )


stock_status.short_description = "Inventory"

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

    extra = 1


# ==========================
# Product
# ==========================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

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
        "price",
        "sale_price",
        "stock",
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

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):

        queryset.update(is_approved=True)

    @admin.action(description="Unapprove selected reviews")
    def unapprove_reviews(self, request, queryset):

        queryset.update(is_approved=False)
