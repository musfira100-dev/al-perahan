import io
import re
from datetime import date

from django.core.files.base import ContentFile
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify
from PIL import Image, ImageOps


def optimise_upload(field_file, max_size=(1600, 2000), quality=88):
    """Re-save an uploaded image as a sharp, web-ready progressive JPEG.

    Fixes phone-camera rotation, limits huge files and keeps full quality so
    pictures never look blurry or pixelated on the site.
    """
    try:
        field_file.open()
        img = Image.open(field_file)
        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (250, 246, 238))
            rgba = img.convert("RGBA")
            bg.paste(rgba, mask=rgba.split()[-1])
            img = bg
        else:
            img = img.convert("RGB")
        img.thumbnail(max_size, Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=quality, optimize=True, progressive=True, subsampling=0)
        name = field_file.name.rsplit(".", 1)[0].split("/")[-1] + ".jpg"
        field_file.save(name, ContentFile(buf.getvalue()), save=False)
    except Exception:
        # If anything goes wrong keep the original upload untouched.
        pass


def make_srcset(url, widths=(480, 800, 1200, 1600)):
    """Responsive sizes for web images (Unsplash). Uploaded files return an empty string."""
    if not url or "images.unsplash.com" not in url:
        return ""
    parts = []
    for w in widths:
        parts.append(re.sub(r"([?&])w=\d+", lambda m, w=w: "%sw=%d" % (m.group(1), w), url) + " %dw" % w)
    return ", ".join(parts)


class ImageSourceMixin:
    @property
    def image_src(self):
        return self.image.url if self.image else self.image_url

    @property
    def srcset(self):
        return make_srcset(self.image_src)


class Category(ImageSourceMixin, models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    blurb = models.CharField(max_length=220, blank=True)
    image = models.ImageField(upload_to="categories/", blank=True)
    image_url = models.URLField(blank=True, help_text="Optional: use a web image instead of an upload.")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Sale(models.Model):
    """A sale you switch ON only when you want it. Untick 'is active' and prices go back to normal."""
    title = models.CharField(max_length=80, help_text="Shown in the top bar, e.g. Winter Sale")
    percent_off = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(90)],
        help_text="Percent taken off every product in the sale. 0 = only products with their own sale price.")
    categories = models.ManyToManyField(
        Category, blank=True, help_text="Leave empty to put every category on sale.")
    starts_at = models.DateTimeField(null=True, blank=True, help_text="Optional. Empty = starts as soon as it is active.")
    ends_at = models.DateTimeField(null=True, blank=True, help_text="Optional. Shows a countdown in the top bar. Empty = no end date.")
    is_active = models.BooleanField(default=False, help_text="Tick = sale is ON. Untick = sale is OFF.")

    class Meta:
        ordering = ["-is_active", "-id"]

    def __str__(self):
        return self.title

    @cached_property
    def category_ids(self):
        return {c.id for c in self.categories.all()}

    def applies_to(self, product):
        return not self.category_ids or product.category_id in self.category_ids

    @classmethod
    def live(cls):
        """The sale that is switched on right now, or None."""
        now = timezone.now()
        for s in cls.objects.filter(is_active=True).prefetch_related("categories"):
            if (not s.starts_at or s.starts_at <= now) and (not s.ends_at or s.ends_at > now):
                return s
        return None


class Product(ImageSourceMixin, models.Model):
    title = models.CharField(max_length=140)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    tag = models.CharField(max_length=60, blank=True, help_text="Small label, e.g. Bestseller")
    price_pkr = models.PositiveIntegerField("Price (PKR)")
    sale_price = models.PositiveIntegerField(
        "Sale price (PKR)", null=True, blank=True,
        help_text="Optional. Used only while a sale is ON. Empty = the sale's percent off is used.")
    fabric = models.CharField(max_length=140, blank=True)
    craft = models.CharField(max_length=160, blank=True)
    delivery = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    sizes = models.CharField(
        max_length=120, default="S,M,L,XL",
        help_text="Comma separated, e.g. 38,40,42,44 or Single,Double,King or Window,Door",
    )
    image = models.ImageField(
        upload_to="products/", blank=True,
        help_text="Best: portrait photo, at least 1200 x 1600 px. It is optimised automatically.",
    )
    image_url = models.URLField(blank=True, help_text="Optional: web image link if you do not upload one.")
    is_featured = models.BooleanField(default=False, help_text="Featured products are listed first.")
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_featured", "id"]

    def __str__(self):
        return self.title

    def price_for(self, sale):
        """Price to charge right now (normal price unless a live sale applies)."""
        if sale and sale.applies_to(self):
            if self.sale_price:
                return min(self.sale_price, self.price_pkr)
            if sale.percent_off:
                return int(round(self.price_pkr * (100 - sale.percent_off) / 100))
        return self.price_pkr

    @property
    def size_list(self):
        return [x.strip() for x in self.sizes.split(",") if x.strip()] or ["One size"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:130]
        if self.image and not getattr(self.image, "_committed", True):
            optimise_upload(self.image)
        super().save(*args, **kwargs)


class HeroSlide(ImageSourceMixin, models.Model):
    """Homepage banners. 'Home top slider' = big banner at the top. 'Two-banner row' = the two side by side."""
    PLACEMENTS = [("hero", "Home top slider"), ("split", "Two-banner row")]
    placement = models.CharField(max_length=6, choices=PLACEMENTS, default="hero")
    eyebrow = models.CharField(max_length=60, blank=True, help_text="Small line above the title, e.g. NEW IN")
    title = models.CharField(max_length=120)
    text = models.CharField(max_length=260, blank=True)
    image = models.ImageField(upload_to="hero/", blank=True)
    image_url = models.URLField(blank=True)
    button_label = models.CharField(max_length=40, default="Shop now")
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL,
                                 help_text="Button opens this category.")
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["placement", "order", "id"]
        verbose_name = "banner"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.image and not getattr(self.image, "_committed", True):
            optimise_upload(self.image, max_size=(2600, 2600), quality=90)
        super().save(*args, **kwargs)


class Showroom(ImageSourceMixin, models.Model):
    city = models.CharField(max_length=60)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=220)
    hours = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    image = models.ImageField(upload_to="showrooms/", blank=True)
    image_url = models.URLField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.city} - {self.title}"

    def save(self, *args, **kwargs):
        if self.image and not getattr(self.image, "_committed", True):
            optimise_upload(self.image, max_size=(2000, 1500))
        super().save(*args, **kwargs)


class Testimonial(models.Model):
    quote = models.TextField()
    name = models.CharField(max_length=80)
    place = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS = [
        ("placed", "Order received"),
        ("finishing", "In hand-finishing"),
        ("quality", "Quality check"),
        ("dispatched", "Dispatched"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    reference = models.CharField(max_length=24, unique=True, blank=True, editable=False)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    city = models.CharField(max_length=80)
    address = models.TextField()
    notes = models.TextField(blank=True)
    total_pkr = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=12, choices=STATUS, default="placed")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.reference or 'New'} - {self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.reference:
            self.reference = f"ALP-{date.today().year}-{1000 + self.pk}"
            super().save(update_fields=["reference"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=140)
    size = models.CharField(max_length=20, default="M")
    quantity = models.PositiveSmallIntegerField(default=1)
    price_pkr = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} x{self.quantity}"

    @property
    def line_total(self):
        return self.price_pkr * self.quantity


class BespokeRequest(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    service = models.CharField(max_length=120)
    preferred_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    handled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "appointment request"

    def __str__(self):
        return f"{self.name} - {self.service}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.email
