from .models import Category, SiteSettings


def global_data(request):
    return {
        "categories": Category.objects.filter(is_active=True).order_by("sort_order"),
        "site_settings": SiteSettings.objects.first(),
    }