# Generated by Django 4.2.16 on 2024-10-23 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0008_alter_podcast_apple_music_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podcast',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='podcasts', to='podcasts.tag'),
        ),
    ]
