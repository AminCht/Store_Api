# Generated by Django 4.0.6 on 2022-08-02 02:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_alter_customer_options_remove_customer_email_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['user__first_name'], 'permissions': [('cancel_order', 'can cancel order')]},
        ),
    ]