# Generated by Django 4.1.2 on 2022-10-11 16:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_address_zip'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='membership_type',
            new_name='payment_status',
        ),
    ]