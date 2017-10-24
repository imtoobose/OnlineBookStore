from django.contrib import admin
from .models import Book
from .models import UserProfile
from .models import ContactForm
admin.site.register(Book)
admin.site.register(UserProfile)
admin.site.register(ContactForm)