from django.contrib import admin
from .models import Book
from .models import UserProfile
admin.site.register(Book)
admin.site.register(UserProfile)
