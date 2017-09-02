# Python imports
import os
import pickle
import time
from dateutil import parser as date_parser
import json
from PIL import Image
from lxml import etree
from lxml.html.clean import Cleaner
import requests

# Django imports
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# User defined module imports
from .models import Book, UserProfile, Rating
from .modules.epubtotext import convert, __get_extension__, __get_file_name__
from .modules.epubnlp import get_nlp_features


nlp = None


def home(req):
	return render(req, 'home.html', {})


def get_books(req):
    books = Book.objects.all()
    send_data = {'data': []}
    for book in books:
        bdict = book.to_dict()
        bdict['url'] = book.get_url()
        send_data['data'].append(bdict)

    return JsonResponse(send_data)


def upload_book(req):
	global nlp

	if req.method == 'GET':
		return render(req, 'uploadform.html', {})

	elif req.method == 'POST':
		# Load spacy and NLP model
		print('Loading Spacy')
		import spacy
		if nlp == None:
			nlp = spacy.load('en')
		print('Done loading Spacy')

		# Read uploaded file and save to disk
		f = req.FILES['book']
		fname = f.name
		media_path = os.path.join(os.getcwd(), 'bookstoreapp', 'media') 
		with open(os.path.join(media_path, 'books', fname), 'wb+') as destination:
			for chunk in f.chunks():
				destination.write(chunk)


		# Convert EPUB file to folder with raw text
		p = os.path.join(media_path, 'books', fname)
		pro = os.path.dirname(convert(p, output_file=os.path.join(media_path, 
													'processed' , 
													__get_file_name__(fname), 
													__get_file_name__(fname) +
													'.txt')))
		

		# Get meta dict for extracted EPUB
		with open(os.path.join(pro, 'meta.pkl'), 'rb') as metaf:
			meta = pickle.load(metaf)

		# Extract cover image and save in thumbnail resolution
		img = None
		if not meta['cover'] == None:
			iname = 'photos' + '/' +\
							'{0}-{1}{2}'.format(fname, 
											int(time.time()),
											__get_extension__(meta['cover']))

			img = os.path.join(media_path, iname)
			im = Image.open(os.path.join(pro, meta['cover']))
			im.thumbnail((350, 350))
			im.save(img)

		else:
			iname = os.path.join('photos', 'placeholder.png')


		# Set Publisher date
		if meta['pub_date'] == '':
			pub_date = None
		else:
			pub_date = date_parser.parse(meta['pub_date'])
			print(meta['pub_date'])


		# Get number of verbs per chapter, NERs
		print('Creating NLP features')
		verbs, ners = get_nlp_features(pro, nlp)
		print('Done with NLP features')
		print(verbs, ners)


		# Save to DB
		book = Book(
					title=meta['title'],
					author=meta['author'],
					description=meta['description'],
					language=meta['language'],
					pub_date=pub_date,
					publication=meta['publication'],
					genre=meta['subjects'],
					image_link=(settings.MEDIA_URL + iname),
					graph_data=json.dumps(verbs),
					ners=json.dumps(ners.most_common(20)),
					epub_link=(settings.MEDIA_URL + os.path.join('books', fname)),
				)

		book.save()
		return redirect(home)

def get_author_description(author):
	url = ('https://en.wikipedia.org/w/api.php?format=xml&action=query&'
		   'prop=extracts%7Cpageimages&exintro=&explaintext=&'
		   'titles=' + author + '&redirects=1&piprop=original')

	r = requests.get(url)

	desc = ''
	author_photo = ''

	if r.status_code == 200:
		root = etree.fromstring(r.content)
		desc = root.find('.//extract').text
		author_photo = root.find('.//original').attrib['source']

	return desc, author_photo


def view_book(req, book_id):
    book = get_object_or_404(Book, pk=book_id)
    bdict = book.to_dict()
    return JsonResponse(bdict)


def view_book_html(req, book_id, book_slug):
    return render(req, 'book.html', {
        'id': book_id,
        'book_name': ' '.join(book_slug.split('-')).title()
    })


def contact(request):
    return render(request, 'contact.html', {})


def about(request):
    return render(request, 'about.html', {})


def signup(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            return redirect(home)
        else:
            return render(request, 'signup.html', {})
    
    elif request.method == 'POST':
        username = request.POST['name']
        password = request.POST['pass']
        roll_no = request.POST['roll']
        email = request.POST['email']

        user = User.objects.create_user(username=roll_no,
                                         email=email,
                                         password=password)
        user.save()

        userProfile = UserProfile(
                        user=user,
                        name=username
                      )

        userProfile.save()

        return redirect(reverse('login'))


def signin(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            return redirect(home)

        else:
            return render(request, 'login.html', {})

    elif request.method == 'POST':
        username = request.POST['name']
        password = request.POST['pass']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('home'))

        else:
            print ("Invalid login details: {0}, {1}".format(username, password))
            return redirect(reverse('login'))

        return redirect(reverse('home'))


def signout(request):
    if request.user.is_authenticated():
        logout(request)
        return redirect(reverse('home'))