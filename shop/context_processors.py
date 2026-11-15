from .models import SiteSettings


def brand(request):
    site = SiteSettings.get_solo()
    return {
        "SITE": site,
        "BRAND_NAME": site.name,
        "BRAND_PHONE": site.phone,
        "BRAND_EMAIL": site.email,
        "WHATSAPP_NUMBER": site.whatsapp_number,
    }
