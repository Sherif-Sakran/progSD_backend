# Generated by Django 5.1.2 on 2024-11-05 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_customuser_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerprofile',
            name='discount_valid_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
