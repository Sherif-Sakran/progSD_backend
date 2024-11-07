# Generated by Django 5.1.2 on 2024-11-04 21:09

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0009_vehicle_make_vehicle_model'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountRequests',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('student_id_number', models.CharField(max_length=20)),
                ('institution', models.CharField(max_length=100)),
                ('student_email', models.EmailField(max_length=254)),
                ('request_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('response_by_operator', models.TextField(null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('confirmed_date', models.DateTimeField(blank=True, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
