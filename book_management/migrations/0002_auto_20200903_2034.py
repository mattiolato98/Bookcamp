# Generated by Django 3.1 on 2020-09-03 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover_image_file',
            field=models.ImageField(default='static/img/prova.jpg', upload_to='books_cover/'),
        ),
    ]
