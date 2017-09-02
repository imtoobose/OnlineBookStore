from __future__ import unicode_literals

from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.shortcuts import reverse
import os
import time
from copy import copy

def __get_book_path__(filename):
	return os.path.join('photos', int(time.time()), filename)


def __convert_to_dict__(obj):
    dic = copy(obj.__dict__)
    
    try:
        del dic['_state']
    except KeyError:
        pass

    return dic


class Book(models.Model):
    author = models.CharField(max_length=300, default="", null=True)
    title = models.CharField(max_length=1000, default="", null=True)
    description = models.TextField(default="", null=True)
    language = models.CharField(max_length=30, default="en", null=True)
    publication = models.CharField(max_length=1000, default="", null=True)
    pub_date = models.DateField(default=None, null=True)
    image_link = models.CharField(default=None, max_length=1000, null=True)
    active = models.BooleanField(default=True)
    genre = models.TextField(default="", blank=True)
    slug = models.SlugField(max_length=100, editable=False, default='unnamed-book')
    graph_data = models.TextField(default=None, null=True, blank=True)
    ners = models.TextField(default=None, null=True, blank=True)
    rating = models.FloatField(default=0.0, null=True, blank=True)
    num_ratings = models.IntegerField(default=0, null=True, blank=True)
    epub_link = models.CharField(default=None, max_length=1000, null=True, blank=True)
    folder_link = models.CharField(default=None, max_length=1000, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title[:75]
                            if len(self.title) >
                            75 else self.title)

        super(Book, self).save(*args, **kwargs)

    def get_url(self):
        return reverse('view-book', args=(self.id, self.slug, ))

    def __str__(self):
        return self.title + '-' + self.author

    def to_dict(self):
        return __convert_to_dict__(self)

    def update_ratings(self, rating):
        self.rating = (self.rating * self.num_ratings + rating)/(self.num_ratings + 1)
        self.num_ratings += 1
        super(Book, self).save()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class Rating(models.Model):
    rating = models.FloatField(default=0.0, null=True, blank=True)
    user = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, null=True, blank=True, on_delete=models.CASCADE)
