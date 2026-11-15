from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(blank=True, max_length=80, verbose_name='Brand name')),
                ('phone', models.CharField(blank=True, max_length=40, verbose_name='Phone number (shown on site)')),
                ('whatsapp_number', models.CharField(blank=True, max_length=20, verbose_name='WhatsApp number')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('address', models.CharField(blank=True, max_length=250, verbose_name='Address / location')),
                ('maps_url', models.URLField(blank=True, max_length=500, verbose_name='Google Maps link')),
                ('hours', models.CharField(blank=True, max_length=120, verbose_name='Opening hours')),
                ('facebook_url', models.URLField(blank=True, verbose_name='Facebook link')),
                ('instagram_url', models.URLField(blank=True, verbose_name='Instagram link')),
                ('tiktok_url', models.URLField(blank=True, verbose_name='TikTok link')),
                ('youtube_url', models.URLField(blank=True, verbose_name='YouTube link')),
                ('twitter_url', models.URLField(blank=True, verbose_name='X (Twitter) link')),
            ],
            options={
                'verbose_name': 'site settings',
                'verbose_name_plural': 'site settings',
            },
        ),
    ]
