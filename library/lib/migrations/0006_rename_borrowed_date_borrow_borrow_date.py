# Generated by Django 4.2.4 on 2023-08-31 04:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lib', '0005_borrow_return_date_fact_alter_borrow_return_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='borrow',
            old_name='borrowed_date',
            new_name='borrow_date',
        ),
    ]
