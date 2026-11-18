from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from .models import (BespokeRequest, Category, HeroSlide, Order, OrderItem, Product,
                     Sale, Showroom, SiteSettings, Subscriber, Testimonial)


def thumb(obj):
    src = obj.image_src
    if not src:
        return "-"
    return format_html('<img src="{}" style="height:56px;width:44px;object-fit:cover;border-radius:4px">', src)


thumb.short_description = "Photo"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Main menu categories and their sub-categories (set 'Parent' to make a sub-category, e.g. Men's Suits > Summer)."""
    list_display = (thumb, "menu_name", "parent", "order")
    list_display_links = (thumb, "menu_name")
    list_editable = ("order",)
    list_filter = ("parent",)
    search_fields = ("name",)
    fields = ("name", "parent", "blurb", "image", "image_url", "order", "slug")

    @admin.display(description="Name", ordering="name")
    def menu_name(self, obj):
        return f"- {obj.name}" if obj.parent_id else obj.name

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("parent")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (thumb, "title", "category", "price_pkr", "sale_price", "tag", "is_featured", "is_active")
    list_filter = ("category", "is_active", "is_featured")
    list_editable = ("price_pkr", "sale_price", "tag", "is_featured", "is_active")
    search_fields = ("title", "fabric", "craft", "description")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "tag", "is_featured", "is_active")}),
        ("Price", {"fields": ("price_pkr", "sale_price")}),
        ("Sizes", {"description": "Choose Letters (S, M, L...) or Numbers (38, 40...) - or Custom to type your own list.",
                   "fields": ("size_preset", "sizes")}),
        ("Photo", {"fields": ("image", "image_url")}),
        ("Details", {"fields": ("fabric", "craft", "delivery", "description")}),
    )


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """Switch a sale ON or OFF with one tick. When it is OFF the site shows normal prices only."""
    list_display = ("title", "percent_off", "is_active", "starts_at", "ends_at")
    list_editable = ("is_active",)
    filter_horizontal = ("categories",)
    actions = ["switch_on", "switch_off"]

    @admin.action(description="Switch selected sale ON")
    def switch_on(self, request, qs):
        qs.update(is_active=True)

    @admin.action(description="Switch selected sale OFF")
    def switch_off(self, request, qs):
        qs.update(is_active=False)


@admin.register(HeroSlide)
class BannerAdmin(admin.ModelAdmin):
    list_display = (thumb, "title", "placement", "category", "order", "is_active")
    list_editable = ("placement", "order", "is_active")
    list_filter = ("placement", "is_active")


@admin.register(Showroom)
class ShowroomAdmin(admin.ModelAdmin):
    list_display = ("city", "title", "address", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "place", "order", "is_active")
    list_editable = ("order", "is_active")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "title", "size", "quantity", "price_pkr")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "name", "phone", "city", "total_pkr", "status", "created")
    list_filter = ("status", "created")
    list_editable = ("status",)
    search_fields = ("reference", "name", "phone", "email")
    readonly_fields = ("reference", "total_pkr", "created")
    inlines = [OrderItemInline]
    actions = ["mark_finishing", "mark_dispatched", "mark_delivered"]

    @admin.action(description="Mark selected: In hand-finishing")
    def mark_finishing(self, request, qs):
        qs.update(status="finishing")

    @admin.action(description="Mark selected: Dispatched")
    def mark_dispatched(self, request, qs):
        qs.update(status="dispatched")

    @admin.action(description="Mark selected: Delivered")
    def mark_delivered(self, request, qs):
        qs.update(status="delivered")


@admin.register(BespokeRequest)
class BespokeRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "service", "preferred_date", "handled", "created")
    list_filter = ("handled", "service")
    list_editable = ("handled",)
    search_fields = ("name", "phone")


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "created")
    search_fields = ("email",)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Contact details, location and social links. There is only one settings page."""
    fieldsets = (
        ("Brand and contact", {
            "description": "Shown in the top bar, footer and WhatsApp buttons.",
            "fields": ("brand_name", "phone", "whatsapp_number", "email"),
        }),
        ("Location", {
            "description": "Shown in the footer. Paste the link from Google Maps > Share to get a map button.",
            "fields": ("address", "maps_url", "hours"),
        }),
        ("Social links", {
            "description": "Paste the full link (https://...). Leave blank to hide that icon.",
            "fields": ("facebook_url", "instagram_url", "tiktok_url", "youtube_url", "twitter_url"),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.get_solo()
        if not obj.pk or not SiteSettings.objects.filter(pk=obj.pk).exists():
            obj.save()
        return redirect(reverse("admin:shop_sitesettings_change", args=[obj.pk]))
