# Generated by Django 2.2.12 on 2020-05-18 12:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=200)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category', to='blog.Post')),
            ],
        ),
    ]
