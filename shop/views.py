import json
import re
from datetime import datetime
from functools import wraps
from urllib.parse import quote

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import (BespokeRequest, Category, HeroSlide, Order, OrderItem, Product,
                     Sale, Showroom, SiteSettings, Subscriber, Testimonial)

PHONE_RE = re.compile(r"^[0-9+\-\s()]{7,20}$")


# --------------------------------------------------------------- helpers
def throttle(limit=12, window=60):
    """Very small per-IP rate limit for the public POST endpoints."""
    def deco(view):
        @wraps(view)
        def inner(request, *args, **kwargs):
            ip = request.META.get("REMOTE_ADDR", "x")
            key = f"thr:{view.__name__}:{ip}"
            hits = cache.get(key, 0)
            if hits >= limit:
                return JsonResponse({"ok": False, "error": "Too many requests. Please wait a minute."}, status=429)
            cache.set(key, hits + 1, window)
            return view(request, *args, **kwargs)
        return inner
    return deco


def body(request):
    try:
        data = json.loads(request.body or b"{}")
        return data if isinstance(data, dict) else {}
    except (ValueError, UnicodeDecodeError):
        return {}


def clean(value, limit):
    return str(value or "").strip()[:limit]


# ------------------------------------------------------------------ pages
@ensure_csrf_cookie
def home(request):
    sale = Sale.live()
    products = list(Product.objects.filter(is_active=True).select_related("category"))
    product_data = []
    for p in products:
        price = p.price_for(sale)
        was = p.price_pkr if price < p.price_pkr else 0
        product_data.append({
            "id": p.id,
            "title": p.title,
            "category": p.category.name,
            "categorySlug": p.category.slug,
            "tag": p.tag,
            "price": price,
            "was": was,
            "pct": round((was - price) * 100 / was) if was else 0,
            "fabric": p.fabric,
            "craft": p.craft,
            "delivery": p.delivery,
            "desc": p.description,
            "sizes": p.size_list,
            "image": p.image_src,
            "srcset": p.srcset,
            "featured": p.is_featured,
        })
    cat_data = []
    for c in Category.objects.all():
        live = [p for p in product_data if p["categorySlug"] == c.slug]
        cat_data.append({
            "id": c.id, "name": c.name, "slug": c.slug, "blurb": c.blurb, "image": c.image_src, "srcset": c.srcset,
            "count": len(live), "start": min((p["price"] for p in live), default=0),
        })
    showrooms = [
        {"city": s.city, "title": s.title, "desc": s.description, "address": s.address,
         "hours": s.hours, "phone": s.phone, "image": s.image_src, "srcset": s.srcset}
        for s in Showroom.objects.filter(is_active=True)
    ]

    def banner(b):
        return {"eyebrow": b.eyebrow, "title": b.title, "text": b.text, "image": b.image_src, "srcset": b.srcset,
                "label": b.button_label, "slug": b.category.slug if b.category else "all"}

    banners = list(HeroSlide.objects.filter(is_active=True).select_related("category"))
    sale_data = None
    if sale:
        sale_data = {
            "title": sale.title,
            "percent": sale.percent_off,
            "endsAt": sale.ends_at.isoformat() if sale.ends_at else "",
            "count": sum(1 for p in product_data if p["was"]),
        }
    hero_slides = [banner(b) for b in banners if b.placement == "hero"]
    if len(hero_slides) < 2:
        # Not enough banners yet: fill the slider from the categories so it always slides.
        for c in cat_data:
            if len(hero_slides) >= 4:
                break
            hero_slides.append({"eyebrow": "SHOP", "title": c["name"], "text": c["blurb"], "image": c["image"],
                                "srcset": c["srcset"], "label": "Shop " + c["name"], "slug": c["slug"]})
    context = {
        "sale": sale_data,
        "hero_slides": hero_slides,
        "split_banners": [banner(b) for b in banners if b.placement == "split"][:2],
        "categories": cat_data,
        "testimonials": Testimonial.objects.filter(is_active=True),
        "shop_data": {
            "products": product_data,
            "categories": cat_data,
            "showrooms": showrooms,
            "sale": sale_data,
            "whatsapp": SiteSettings.get_solo().whatsapp_number,
        },
    }
    return render(request, "shop/home.html", context)


# -------------------------------------------------------------------- API
@require_POST
@throttle(limit=8)
def api_checkout(request):
    data = body(request)
    if data.get("website"):  # honeypot
        return JsonResponse({"ok": True, "reference": "ALP-0000"})

    name = clean(data.get("name"), 100)
    phone = clean(data.get("phone"), 30)
    city = clean(data.get("city"), 80)
    address = clean(data.get("address"), 500)
    email = clean(data.get("email"), 120)
    notes = clean(data.get("notes"), 500)

    errors = {}
    if len(name) < 2:
        errors["name"] = "Please enter your full name."
    if not PHONE_RE.match(phone):
        errors["phone"] = "Enter a valid phone / WhatsApp number."
    if len(city) < 2:
        errors["city"] = "Please enter your city."
    if len(address) < 8:
        errors["address"] = "Please enter your full delivery address."
    if email:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "This email address does not look right."

    raw_items = data.get("items")
    if not isinstance(raw_items, list) or not raw_items or len(raw_items) > 30:
        errors["items"] = "Your bag is empty."
    if errors:
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    wanted = {}
    for it in raw_items:
        try:
            pid, qty = int(it.get("id")), int(it.get("qty", 1))
        except (TypeError, ValueError, AttributeError):
            continue
        size = clean(it.get("size"), 20)
        qty = max(1, min(qty, 10))
        wanted[(pid, size)] = wanted.get((pid, size), 0) + qty

    products = {p.id: p for p in Product.objects.filter(id__in={k[0] for k in wanted}, is_active=True)}
    lines = []
    for (pid, size), qty in wanted.items():
        prod = products.get(pid)
        if prod:
            lines.append((prod, size if size in prod.size_list else prod.size_list[0], qty))
    if not lines:
        return JsonResponse({"ok": False, "errors": {"items": "These items are no longer available."}}, status=400)

    sale = Sale.live()
    with transaction.atomic():
        order = Order.objects.create(
            name=name, phone=phone, email=email, city=city, address=address, notes=notes,
            total_pkr=sum(p.price_for(sale) * q for p, _, q in lines),
        )
        OrderItem.objects.bulk_create([
            OrderItem(order=order, product=p, title=p.title, size=s, quantity=q, price_pkr=p.price_for(sale))
            for p, s, q in lines
        ])

    summary = "\n".join(f"- {p.title} ({s}) x{q}" for p, s, q in lines)
    site = SiteSettings.get_solo()
    text = (f"Hello {site.name}, I placed order {order.reference}.\n{summary}\n"
            f"Total: PKR {order.total_pkr:,}\nName: {name}\nCity: {city}")
    return JsonResponse({
        "ok": True,
        "reference": order.reference,
        "total": order.total_pkr,
        "whatsapp": f"https://wa.me/{site.whatsapp_number}?text={quote(text)}",
    })


@require_GET
@throttle(limit=30)
def api_track(request):
    ref = clean(request.GET.get("ref"), 24).upper()
    order = Order.objects.filter(reference=ref).first()
    if not order:
        return JsonResponse({"ok": False, "error": "We could not find that order reference."}, status=404)
    steps = [s for s in Order.STATUS if s[0] != "cancelled"]
    keys = [s[0] for s in steps]
    current = keys.index(order.status) if order.status in keys else -1
    return JsonResponse({
        "ok": True,
        "reference": order.reference,
        "status": order.status,
        "statusLabel": order.get_status_display(),
        "cancelled": order.status == "cancelled",
        "placed": order.created.strftime("%d %b %Y"),
        "steps": [{"key": k, "label": l, "done": i <= current} for i, (k, l) in enumerate(steps)],
    })


@require_POST
@throttle(limit=6)
def api_bespoke(request):
    data = body(request)
    if data.get("website"):
        return JsonResponse({"ok": True})
    name, phone = clean(data.get("name"), 100), clean(data.get("phone"), 30)
    errors = {}
    if len(name) < 2:
        errors["name"] = "Please enter your name."
    if not PHONE_RE.match(phone):
        errors["phone"] = "Enter a valid phone / WhatsApp number."
    if errors:
        return JsonResponse({"ok": False, "errors": errors}, status=400)
    when = None
    if data.get("date"):
        try:
            when = datetime.strptime(clean(data.get("date"), 10), "%Y-%m-%d").date()
        except ValueError:
            when = None
    BespokeRequest.objects.create(
        name=name, phone=phone, service=clean(data.get("service"), 120) or "Consultation",
        preferred_date=when, notes=clean(data.get("notes"), 800),
    )
    return JsonResponse({"ok": True})


@require_POST
@throttle(limit=6)
def api_newsletter(request):
    data = body(request)
    if data.get("website"):
        return JsonResponse({"ok": True})
    email = clean(data.get("email"), 120).lower()
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"ok": False, "error": "Please enter a valid email address."}, status=400)
    _, created = Subscriber.objects.get_or_create(email=email)
    return JsonResponse({"ok": True, "created": created})
