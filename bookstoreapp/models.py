from __future__ import unicode_literals
from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.shortcuts import reverse
from django.conf import settings
import os
import time
from copy import copy
import requests
from lxml import etree
from PIL import Image

def __get_book_path__(filename):
	return os.path.join('photos', int(time.time()), filename)

print(settings.MEDIA_ROOT)
def __convert_to_dict__(obj):
    dic = copy(obj.__dict__)
    
    try:
        del dic['_state']
    except KeyError:
        pass

    return dic


class Genre(models.Model):
    genre = models.TextField(null=True, blank=True, default="")
    def __str__(self):
        return self.genre


class Author(models.Model):
    name = models.CharField(max_length=30000, default="Unknown", null=True)
    description = models.TextField(default="", null=True, blank=True)
    photo_url = models.TextField(default="", null=True, blank=True)


    def __str__(self):
        return self.name


    def to_dict(self):
        dic = __convert_to_dict__(self)
        return dic

    def generate_url(self, author, try_no):
        if try_no == 2:
            author += ' (author)'
        elif try_no == 3:
            author += ' (writer)'

        url = ('https://en.wikipedia.org/w/api.php?format=xml&action=query&'
               'prop=extracts%7Cpageimages&exintro=&explaintext=&'
               'titles=' + author + '&redirects=1&piprop=original')

        print('GENERATE', url)
        return url


    def get_author_description(self, author):
        url = ('https://en.wikipedia.org/w/api.php?format=xml&action=query&'
               'prop=extracts%7Cpageimages&exintro=&explaintext=&'
               'titles=' + author + '&redirects=1&piprop=original')

        r = requests.get(url)

        desc = ''
        author_photo = ''

        if r.status_code == 200:
            root = etree.fromstring(r.content)
            desc = root.find('.//extract').text
            try_no = 1
            photo_elem = root.find('.//original')

            while True:
                root = etree.fromstring(r.content)
                desc = root.find('.//extract').text
                if photo_elem is not None:
                    author_photo = photo_elem.attrib['source']
                    break

                else:
                    print("HELLOOO")
                    try_no += 1
                    r = requests.get(self.generate_url(author, try_no))
                    photo_elem = root.find('.//original')
                    if try_no == 3:
                        break

            if len(author_photo) > 0:
                imr = requests.get(author_photo, stream=True)
                author_photo_path = os.path.join(settings.MEDIA_ROOT, 'authors', 
                                    os.path.basename(author_photo))

                if imr.status_code == 200:
                    with open(author_photo_path, 'wb') as f:
                        for chunk in imr.iter_content(1024):
                            f.write(chunk)
                    
                    im = Image.open(author_photo_path)
                    im.thumbnail((350, 350))
                    im.save(author_photo_path)
            else:
                author_photo_path = os.path.join(settings.MEDIA_ROOT, 'authors',
                                                'placeholder.jpg')

        return desc, author_photo_path

    def save(self, *args, **kwargs):
        if not self.pk:
            desc, url = self.get_author_description(self.name)
            self.description = desc 
            self.photo_url = url

        super(Author, self).save(*args, **kwargs)


class Book(models.Model):
    author = models.CharField(max_length=300, default="", null=True)
    author_obj = models.ForeignKey(Author, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, default="", null=True, blank=True)
    description = models.TextField(default="", null=True, blank=True)
    language = models.CharField(max_length=30, default="en", null=True, blank=True)
    publication = models.CharField(max_length=1000, default="", null=True)
    pub_date = models.DateField(default=None, null=True)
    image_link = models.CharField(default=None, max_length=1000, null=True)
    active = models.BooleanField(default=True)
    genre = models.TextField(default="", blank=True)
    slug = models.SlugField(max_length=100, editable=False, default='unnamed-book')
    graph_data = models.TextField(default=None, null=True, blank=True)
    ners = models.TextField(default=None, null=True, blank=True)
    avg_rating = models.FloatField(default=0.0, null=True, blank=True)
    num_ratings = models.IntegerField(default=0, null=True, blank=True)
    epub_link = models.CharField(default=None, max_length=1000, null=True, blank=True)
    folder_link = models.CharField(default=None, max_length=1000, null=True, blank=True)
    rating_keywords = models.TextField(default="", null=True, blank=True)
    text_rating_count = models.IntegerField(default=0, null=True, blank=True)
    genres = models.ManyToManyField(Genre)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title[:75]
                            if len(self.title) >
                            75 else self.title)
        
        if self.author_obj is None:
            author = Author.objects.get_or_create(name=self.author)[0]
            self.author_obj = author

        super(Book, self).save(*args, **kwargs)

    def get_url(self):
        return reverse('view-book', args=(self.id, self.slug, ))

    def __str__(self):
        return self.title + '-' + self.author

    def to_dict(self):
        dic = __convert_to_dict__(self)
        dic['url'] = self.get_url()
        return dic

    def update_ratings(self, new_rating, old_rating=-1.0):
        if old_rating == -1.0:
            self.avg_rating = (self.avg_rating * self.num_ratings + new_rating)/(self.num_ratings + 1)
            self.num_ratings += 1
        else:
            self.avg_rating = (self.avg_rating * self.num_ratings + new_rating - old_rating)/(self.num_ratings) 
        super(Book, self).save()
        return self.avg_rating


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    active = models.BooleanField(default=True)
    is_faculty = models.BooleanField(default=False)
    name = models.CharField(default='Anonymous', max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    read_books = models.ManyToManyField(Book)


class Rating(models.Model):
    rating = models.FloatField(default=0.0, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, null=True, blank=True, on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)