# Generated by Django 2.2.12 on 2020-05-19 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='expense_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]