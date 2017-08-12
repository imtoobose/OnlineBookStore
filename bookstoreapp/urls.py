from django.conf.urls import url, include
from . import views
urlpatterns = [
	url(r'^view-book/(?P<book_id>\d+)/(?P<book_slug>[\w-]+)/$', views.view_book, name='view-book'),
	url(r'^get-all-books/$', views.get_books, name='get-all'),
	url(r'^upload-book/$', views.upload_book, name='upload-book'),
	url(r'^$', views.home, name='home'),
]