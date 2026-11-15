 # Al Perahan Collection - Django store (Men's Suits, Parda, Clothing, Bed Sheets)

Colors logo se: teal #026A6B + gold #D19B53.

## Pehli dafa
`setup.bat` double-click karein. Ye packages install karta hai, dummy photos banata hai, database banata hai,
dummy products bharta hai aur admin user poochta hai. Site: http://127.0.0.1:8000  Admin: /admin
Dobara chalane ke liye `run.bat`.

## Purani zip se upgrade
`upgrade.bat` chalayein (naye fields ka migration banata hai aur purana bridal data hata kar naya dummy data bharta hai).
Dhyan: isay sirf ek dafa chalayein, warna aap ke upload kiye products dobara hat jayenge.

## Admin se kya karein
- Sales: "Winter Sale" bana hua hai lekin OFF hai. "Is active" tick = sale ON (top bar, countdown, Sale menu,
  sale row, cut price aur -% badge). Untick = sab normal. End date dene se countdown chalta hai.
  Categories chun sakti hain (khali = sab) aur Product mein alag "Sale price" bhi de sakti hain.
- Banners: homepage ka bara slider ("Home top slider") aur do side-by-side banners ("Two-banner row").
- Products / Categories: photo upload karein (khud sharp JPEG ban jati hai). Sizes comma se likhein: 38,40,42 ya Single,Double,King.
- Showroom address, Testimonials, Orders (status badlein), Appointment requests, Subscribers.

## Zaroor badalein
- WhatsApp / phone / email: `config/settings.py` ya environment variables WHATSAPP_NUMBER, BRAND_PHONE, BRAND_EMAIL.
- Dummy photos: `static/img/demo/` (make_demo_images.py banata hai). Asli photos admin se upload karein.
- Live karne se pehle: DJANGO_DEBUG=0, DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS, phir `python manage.py collectstatic`.


<!-- py -3.12 -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python make_demo_images.py
python manage.py makemigrations shop
python manage.py migrate
python manage.py seed_shop
python manage.py createsuperuser
python manage.py runserver -->
## Site settings (admin)
Admin > Site settings: phone, WhatsApp, email, address, Google Maps link, opening hours and social links (Facebook, Instagram, TikTok, YouTube, X). Blank social links are hidden on the site. After pulling this update run `python manage.py migrate`.
