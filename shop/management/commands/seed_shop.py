from django.core.management.base import BaseCommand

from shop.models import Category, HeroSlide, Product, Sale, Showroom, Testimonial

D = "/static/img/demo/{}.jpg"

CATEGORIES = [
    ("Men's Suits", "mens-suits", "Two and three piece suits, tuxedos and summer suits, stitched to your measurements.", "suit-1"),
    ("Parda", "parda", "Velvet, voile and jacquard parda, made to the size of your window or door.", "parda-1"),
    ("Clothing", "clothing", "Shalwar kameez, kurtas and waistcoats for everyday and occasions.", "clothing-1"),
    ("Bed Sheets", "bed-sheets", "Cotton and satin bed sheet sets and comforters in single, double and king.", "sheet-1"),
]

# title, category slug, tag, price, fabric, finish, delivery, sizes, image, description, featured
PRODUCTS = [
    ("Charcoal Wool-Blend Three Piece Suit", "mens-suits", "Bestseller", 38500, "Wool blend", "Notch lapel, half canvas", "7 - 10 days, stitched to size", "38,40,42,44,46,48", "suit-1", "A classic charcoal three piece with jacket, waistcoat and trousers, cut to your measurements.", True),
    ("Navy Pinstripe Two Piece Suit", "mens-suits", "New", 32000, "Suiting fabric", "Pinstripe, two buttons", "7 - 10 days, stitched to size", "38,40,42,44,46,48", "suit-2", "A navy pinstripe two piece for the office and formal events.", False),
    ("Black Formal Tuxedo Set", "mens-suits", "Evening", 42500, "Fine suiting", "Satin peak lapel", "10 - 12 days, stitched to size", "38,40,42,44,46,48", "suit-3", "A black tuxedo set with satin peak lapels for weddings and dinners.", False),
    ("Tan Linen Summer Suit", "mens-suits", "Summer", 27500, "Linen blend", "Unlined, breathable", "7 - 10 days, stitched to size", "38,40,42,44,46,48", "suit-4", "A light tan summer suit that stays cool in hot weather.", False),
    ("Teal Velvet Parda (pair)", "parda", "Bestseller", 14500, "Velvet", "Blackout lining, ring top", "5 - 7 days, stitched to size", "Window,Door,Custom size", "parda-1", "Thick teal velvet parda with a blackout lining. Sold as a pair, stitched to your size.", True),
    ("Ivory Voile Sheer Parda (pair)", "parda", "Light", 6800, "Voile", "Soft sheer, ring top", "5 - 7 days, stitched to size", "Window,Door,Custom size", "parda-2", "Light ivory voile that softens daylight. Pairs well with a heavier parda.", False),
    ("Gold Leaf Jacquard Parda (pair)", "parda", "New", 18900, "Jacquard", "Woven gold pattern, lined", "7 - 10 days, stitched to size", "Window,Door,Custom size", "parda-3", "A rich jacquard parda with a woven gold pattern for drawing rooms.", False),
    ("Sand Linen-Look Parda (pair)", "parda", "", 9500, "Linen-look polyester", "Pleated top, lined", "5 - 7 days, stitched to size", "Window,Door,Custom size", "parda-4", "A relaxed sand parda that suits bedrooms and lounges.", False),
    ("White Cotton Shalwar Kameez", "clothing", "Everyday", 4800, "Cotton", "Collar, side pockets", "3 - 5 days", "S,M,L,XL,XXL", "clothing-1", "A crisp white cotton shalwar kameez for daily wear and Fridays.", False),
    ("Olive Wash & Wear Kurta", "clothing", "", 3900, "Wash & wear", "Front placket", "3 - 5 days", "S,M,L,XL,XXL", "clothing-2", "An easy olive kurta that needs little ironing.", False),
    ("Charcoal Embroidered Waistcoat", "clothing", "Occasion", 8900, "Cotton silk", "Gold trim, lined", "5 - 7 days", "S,M,L,XL", "clothing-3", "A charcoal waistcoat with gold trim to wear over a kurta or shirt.", False),
    ("Camel Premium Wool Shawl", "clothing", "Winter", 6500, "Wool blend", "Fringed edges", "3 - 5 days", "One size", "clothing-4", "A warm camel shawl for cold evenings.", False),
    ("Teal Stripe Cotton Bed Sheet Set", "bed-sheets", "Bestseller", 5900, "Cotton", "1 sheet, 2 pillow covers", "3 - 5 days", "Single,Double,King", "sheet-1", "A cotton bed sheet set in teal stripes with two pillow covers.", True),
    ("Ivory Satin Bed Sheet Set", "bed-sheets", "Soft", 8400, "Satin", "Fitted sheet, 2 pillow covers", "3 - 5 days", "Single,Double,King", "sheet-2", "A smooth ivory satin set that feels cool and soft.", False),
    ("Gold Motif Printed Bed Sheet", "bed-sheets", "New", 4200, "Printed cotton", "1 sheet, 2 pillow covers", "3 - 5 days", "Single,Double,King", "sheet-3", "A cream bed sheet with a small gold motif print.", False),
    ("Charcoal Quilted Comforter Set", "bed-sheets", "Winter", 11900, "Microfibre", "Quilted, 2 pillow covers", "5 - 7 days", "Double,King", "sheet-4", "A warm quilted comforter set in charcoal for winter.", False),
]

# placement, eyebrow, title, text, image, button, category slug
BANNERS = [
    ("hero", "NEW IN", "Suits stitched to your size", "Two and three piece suits, tuxedos and summer suits. Pick the fabric, we cut to your measurements.", "banner-suit", "Shop men's suits", "mens-suits"),
    ("hero", "PARDA", "Parda made for your windows", "Velvet, voile and jacquard parda, stitched to the exact size of your window or door.", "banner-parda", "Shop parda", "parda"),
    ("hero", "BED SHEETS", "Soft sheets for every bed", "Cotton and satin sets in single, double and king, plus warm winter comforters.", "banner-bed", "Shop bed sheets", "bed-sheets"),
    ("split", "", "Jacquard Parda", "Woven gold pattern", "parda-3", "Shop now", "parda"),
    ("split", "", "Pinstripe Suits", "For the office and events", "suit-2", "Shop now", "mens-suits"),
]

# product title -> sale price (only used while a Sale is switched ON)
SALE_PRICES = {
    "Navy Pinstripe Two Piece Suit": 27500,
    "Teal Velvet Parda (pair)": 11900,
    "Teal Stripe Cotton Bed Sheet Set": 4500,
    "White Cotton Shalwar Kameez": 3900,
}

SHOWROOMS = [
    ("Main showroom", "Al Perahan Collection showroom",
     "Visit us to see suiting, parda and bedding in person, get measured and place your order.",
     "Add your showroom address in the admin panel", "Daily, 11:00 AM - 9:00 PM", ""),
]

TESTIMONIALS = [
    ("The suit fit perfectly after the first fitting, and it was ready on the day they promised.", "Customer", "Men's Suits"),
    ("They measured all our windows and the parda hung exactly right. Very neat stitching.", "Customer", "Parda"),
    ("The bed sheets are soft and the colour has not faded after many washes.", "Customer", "Bed Sheets"),
]


class Command(BaseCommand):
    help = "Fill the store with dummy categories and products (use --reset to replace old data)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing products, categories, showrooms and reviews first.")

    def handle(self, *args, **opts):
        if opts["reset"]:
            Product.objects.all().delete()
            Category.objects.all().delete()
            Showroom.objects.all().delete()
            Testimonial.objects.all().delete()
            HeroSlide.objects.all().delete()
        cats = {}
        for i, (name, slug, blurb, img) in enumerate(CATEGORIES):
            cats[slug], _ = Category.objects.update_or_create(
                slug=slug, defaults={"name": name, "blurb": blurb, "image_url": D.format(img), "order": i})
        for i, name in enumerate(["Summer Suits", "Winter Suits", "Wedding Suits"]):
            sub, _ = Category.objects.get_or_create(
                slug="mens-suits-" + name.split()[0].lower(),
                defaults={"name": name, "parent": cats["mens-suits"], "order": i, "blurb": f"{name} stitched to your measurements."})
            cats[sub.slug] = sub
        for title, cat, tag, price, fabric, craft, delivery, sizes, img, desc, feat in PRODUCTS:
            cat = {"Tan Linen Summer Suit": "mens-suits-summer", "Charcoal Wool-Blend Three Piece Suit": "mens-suits-winter",
                   "Black Formal Tuxedo Set": "mens-suits-wedding"}.get(title, cat)
            Product.objects.update_or_create(
                title=title,
                defaults={"category": cats[cat], "tag": tag, "price_pkr": price, "fabric": fabric, "craft": craft,
                          "delivery": delivery, "sizes": sizes, "image_url": D.format(img),
                          "description": desc, "is_featured": feat, "is_active": True})
        for title, price in SALE_PRICES.items():
            Product.objects.filter(title=title).update(sale_price=price)
        if not HeroSlide.objects.exists():
            for i, (place, eyebrow, title, text, img, label, cat) in enumerate(BANNERS):
                HeroSlide.objects.create(placement=place, eyebrow=eyebrow, title=title, text=text, button_label=label,
                                         image_url=D.format(img), category=cats[cat], order=i)
        if not Sale.objects.exists():
            # Created but switched OFF. Tick "is active" in Admin > Sales when you want a sale.
            Sale.objects.create(title="Winter Sale", percent_off=20, is_active=False)
        if not Showroom.objects.exists():
            for i, (city, title, desc, addr, hours, phone) in enumerate(SHOWROOMS):
                Showroom.objects.create(city=city, title=title, description=desc, address=addr, hours=hours,
                                        phone=phone, image_url=D.format("room"), order=i)
        if not Testimonial.objects.exists():
            for i, (q, n, p) in enumerate(TESTIMONIALS):
                Testimonial.objects.create(quote=q, name=n, place=p, order=i)
        self.stdout.write(self.style.SUCCESS("Dummy data ready. Edit or replace it from /admin/."))
