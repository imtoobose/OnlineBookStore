# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-24 16:23
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Unknown', max_length=30000, null=True)),
                ('description', models.TextField(blank=True, default='', null=True)),
                ('photo_url', models.TextField(blank=True, default='', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(default='', max_length=300, null=True)),
                ('title', models.CharField(blank=True, default='', max_length=1000, null=True)),
                ('description', models.TextField(blank=True, default='', null=True)),
                ('language', models.CharField(blank=True, default='en', max_length=30, null=True)),
                ('publication', models.CharField(default='', max_length=1000, null=True)),
                ('pub_date', models.DateField(default=None, null=True)),
                ('image_link', models.CharField(default=None, max_length=1000, null=True)),
                ('active', models.BooleanField(default=True)),
                ('genre', models.TextField(blank=True, default='')),
                ('slug', models.SlugField(default='unnamed-book', editable=False, max_length=100)),
                ('graph_data', models.TextField(blank=True, default=None, null=True)),
                ('ners', models.TextField(blank=True, default=None, null=True)),
                ('avg_rating', models.FloatField(blank=True, default=0.0, null=True)),
                ('num_ratings', models.IntegerField(blank=True, default=0, null=True)),
                ('epub_link', models.CharField(blank=True, default=None, max_length=1000, null=True)),
                ('folder_link', models.CharField(blank=True, default=None, max_length=1000, null=True)),
                ('rating_keywords', models.TextField(blank=True, default='', null=True)),
                ('text_rating_count', models.IntegerField(blank=True, default=0, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('author_obj', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='bookstoreapp.Author')),
            ],
        ),
        migrations.CreateModel(
            name='ContactForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('surname', models.CharField(blank=True, default='Anonymous', max_length=1000, null=True)),
                ('name', models.CharField(blank=True, default='Anonymous', max_length=1000, null=True)),
                ('city', models.CharField(blank=True, default='Anonymous', max_length=1000, null=True)),
                ('email', models.CharField(blank=True, default='Anonymous', max_length=1000, null=True)),
                ('Company', models.CharField(blank=True, default='Anonymous', max_length=1000, null=True)),
                ('CompanyAddress', models.CharField(blank=True, default='Anonymous', max_length=1000, null=True)),
                ('Postcode', models.CharField(blank=True, default='Anonymous', max_length=1000, null=True)),
                ('Message', models.CharField(blank=True, default='Anonymous', max_length=10000, null=True)),
                ('subject', models.CharField(blank=True, default='Anonymous', max_length=1000, null=True)),
                ('Phone', models.CharField(blank=True, default='Anonymous', max_length=1000, null=True)),
                ('function', models.CharField(blank=True, default='Anonymous', max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.TextField(blank=True, default='', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.FloatField(blank=True, default=0.0, null=True)),
                ('text', models.TextField(blank=True, default='', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('book', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bookstoreapp.Book')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('is_faculty', models.BooleanField(default=False)),
                ('name', models.CharField(blank=True, default='Anonymous', max_length=1000, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('read_books', models.ManyToManyField(to='bookstoreapp.Book')),
                ('user', models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='genres',
            field=models.ManyToManyField(to='bookstoreapp.Genre'),
        ),
    ]