# Generated by Django 2.2 on 2020-12-05 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estore', '0003_auto_20201204_2325'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shop_action',
            field=models.IntegerField(default=1, verbose_name='店家操作'),
        ),
    ]