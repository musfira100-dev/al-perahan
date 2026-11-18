import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_sitesettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(blank=True, help_text="Leave empty for a main menu category. Choose e.g. Men's Suits to make this a sub-category (Summer, Winter...).", limit_choices_to={'parent__isnull': True}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='shop.category'),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, help_text='Leave empty - it is made from the name automatically.', unique=True),
        ),
        migrations.AddField(
            model_name='product',
            name='size_preset',
            field=models.CharField(choices=[('custom', 'Custom - type my own sizes below'), ('letters', 'Letters: S, M, L, XL, XXL'), ('numbers', 'Numbers: 38, 40, 42, 44, 46'), ('both', 'Letters and numbers: S-XXL + 38-46'), ('bedding', 'Bedding: Single, Double, King'), ('free', 'One size')], default='custom', help_text='Pick a ready-made list, or choose Custom and type your own sizes in the box below.', max_length=10, verbose_name='Size type'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sizes',
            field=models.CharField(default='S,M,L,XL', help_text='Used when Size type is Custom. Comma separated numbers or letters, e.g. 38,40,42,44 or S,M,L,XL or Single,Double,King', max_length=120),
        ),
        migrations.AlterField(
            model_name='heroslide',
            name='image',
            field=models.ImageField(blank=True, help_text='Best: wide landscape photo, 2400 x 1000 px (keep the subject in the middle/right). It is optimised automatically.', upload_to='hero/'),
        ),
    ]
