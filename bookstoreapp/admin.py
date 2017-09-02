from django.contrib import admin
from .models import Book, UserProfile, Rating
admin.site.register(Book)
admin.site.register(UserProfile)
admin.site.register(Rating)