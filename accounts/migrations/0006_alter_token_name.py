# Generated by Django 4.0.4 on 2022-06-29 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='name',
            field=models.CharField(blank=True, max_length=40, verbose_name='Key'),
        ),
    ]
