from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.shortcuts import reverse
import os
import time

def __get_book_path__(filename):
	return os.path.join('photos', int(time.time()), filename)


def __convert_to_dict__(obj):
    return obj.__dict__


class Book(models.Model):
    author = models.CharField(max_length=30, default="")
    title = models.CharField(max_length=30, default="")
    description = models.TextField(default="")
    language = models.CharField(max_length=3, default="en")
    pub_date = models.DateField(default=None)
    image_link = models.ImageField(upload_to=__get_book_path__, blank=True, null=True)
    active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=75, editable=False, default='unnamed-book')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title[:75]
                            if len(self.title) >
                            75 else self.title)

        super(Book, self).save(*args, **kwargs)

    def get_url(self):
        return reverse('view-book', args=(self.id, self.slug, ))

    def __str__(self):
        return self.title

    def to_dict(self):
        return __convert_to_dict__(self)