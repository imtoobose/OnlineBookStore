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

# User defined module imports
from .models import Book
from .modules.epubtotext import convert, __get_extension__, __get_file_name__
from .modules.epubnlp import get_nlp_features


# Global Variables
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