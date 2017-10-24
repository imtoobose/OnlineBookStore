from django.contrib import admin
from .models import Book, UserProfile, Rating, Genre, Author, ContactForm
admin.site.register(Book)
admin.site.register(UserProfile)
admin.site.register(Rating)
admin.site.register(Genre)
admin.site.register(Author)
admin.site.register(ContactForm)
