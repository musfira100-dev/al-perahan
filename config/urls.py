from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

admin.site.site_header = "Al Perahan Collection"
admin.site.site_title = "Al Perahan Admin"
admin.site.index_title = "Store management"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("shop.urls")),
]

# Uploaded photos (banners, products, categories). Served by Django so they also show when DEBUG is off.
# (If nginx serves /media/ directly, that is faster and takes priority - this is just the safe fallback.)
urlpatterns += [
    re_path(r"^%s(?P<path>.*)$" % settings.MEDIA_URL.lstrip("/"), serve, {"document_root": settings.MEDIA_ROOT}),
]
