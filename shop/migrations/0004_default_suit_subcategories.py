from django.db import migrations
from django.utils.text import slugify

# Sub-categories created under "Men's Suits" so the menu shows them straight away.
SUBS = ["Summer Suits", "Winter Suits", "Wedding Suits"]


def add_suit_subcategories(apps, schema_editor):
    Category = apps.get_model("shop", "Category")
    parent = Category.objects.filter(slug="mens-suits", parent__isnull=True).first()
    if not parent or Category.objects.filter(parent=parent).exists():
        return
    for i, name in enumerate(SUBS):
        slug = slugify(f"{parent.name} {name}")[:70]
        n = 2
        while Category.objects.filter(slug=slug).exists():
            slug = f"{slugify(f'{parent.name} {name}')[:66]}-{n}"
            n += 1
        Category.objects.create(name=name, slug=slug, parent=parent, order=i, image="", image_url="",
                                blurb=f"{name} stitched to your measurements.")


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_subcategories_sizes'),
    ]

    operations = [
        migrations.RunPython(add_suit_subcategories, migrations.RunPython.noop),
    ]
