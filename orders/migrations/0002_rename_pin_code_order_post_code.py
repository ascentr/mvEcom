# Generated by Django 4.2.1 on 2023-07-24 21:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order", old_name="pin_code", new_name="post_code",
        ),
    ]
