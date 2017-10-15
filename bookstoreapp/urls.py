from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^book/(?P<book_id>\d+)/(?P<book_slug>[\w-]+)/$', views.view_book_html, name='view-book'),
    url(r'^get-book/(?P<book_id>\d+)/$', views.view_book, name='get-book-data'),
    url(r'^get-all-books/$', views.get_books, name='get-all'),
    url(r'^upload-book/$', views.upload_book, name='upload-book'),
    url(r'^login/$', views.signin, name='login'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^about/$', views.about, name='about'),
    url(r'^logout/$', views.signout, name='logout'),
    url(r'^update-ratings/$', views.update_ratings, name='update-ratings'),
    url(r'^read/(?P<book_id>\d+)/$', views.read_book, name='read-book'),
    url(r'^add-read-book/$', views.add_read_book, name='add-read-book'),\
    url(r'^genre/(?P<genre>\w+)/$', views.view_book_genre, name='view-genre'),
    url(r'^get-genre/(?P<genre>\w+)/(?P<page>\d+)/$', views.get_book_genre, name='get-genre'),
    url(r'^$', views.home, name='home'),
]
