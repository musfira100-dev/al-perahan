from django.conf import settings


def brand(request):
    return {
        "BRAND_NAME": settings.BRAND_NAME,
        "BRAND_PHONE": settings.BRAND_PHONE,
        "BRAND_EMAIL": settings.BRAND_EMAIL,
        "WHATSAPP_NUMBER": settings.WHATSAPP_NUMBER,
    }
