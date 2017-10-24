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
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage

# User defined module imports
from .models import Book, UserProfile, Rating, Genre, ContactForm
from .modules.epubtotext import convert, __get_extension__, __get_file_name__
from .modules.epubnlp import get_nlp_features
from django.db.models import Q

nlp = None


def home(req):
	return render(req, 'home.html', {})


def get_books(req):
    books = Book.objects.all().order_by('-avg_rating')[:32]
    new_books = Book.objects.all().order_by('-created_at')[:12]
    send_data = {'data': [], 'new_books': []}

    for book in books:
        bdict = book.to_dict()
        # bdict['url'] = book.get_url()
        send_data['data'].append(bdict)

    for book in new_books:
    	bdict = book.to_dict()
    	# bdict['url'] = book.get_url()
    	send_data['new_books'].append(bdict)

    genres = Genre.objects.annotate(num_books=Count('book'))\
    						.order_by('-num_books')[:36]
    
    send_data['genre_books'] = list()
    g_count = 0
    added_books = dict()

    for g in genres:
    	b_count = 0
    	book_list = list()

    	for i in g.book_set.all().order_by('-avg_rating')[:36]:
    		if not i in added_books:
    			added_books[i] = True
    			b_count += 1
    			i_dic = i.to_dict()
    			# i_dic['url'] = i.get_url()
    			book_list.append(i.to_dict())
    			b_count += 1

    			if b_count == 5:
    				break

    	if b_count >= 3:
	    	send_data['genre_books'].append({
	    		'genre': g.__str__(),
				'books': book_list		
	    	})

	    	g_count += 1
	    	if g_count == 5:
	    		break

    return JsonResponse(send_data)


def view_book_genre(req, genre):
	return render(req, 'genre.html', {'genre': genre})


def get_book_genre(req, genre, page):
	if genre == 'all':
		books = Book.objects.all().order_by('-avg_rating')
	else:
		books = get_object_or_404(Genre, genre=genre).book_set.order_by('-avg_rating')

	print('PAGE', page)
	try:
		p = Paginator(books, 18).page(page)

	except EmptyPage:
		return JsonResponse({
			'success': 'false',
			'error': 'EmptyPage'
			})

	data = [b.to_dict() for b in p]
	return JsonResponse({
		'success': 'true',
		'data': data
		})


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
		pro, extract_path = convert(p, output_file=os.path.join(media_path, 
													'processed' , 
													__get_file_name__(fname), 
													__get_file_name__(fname) +
													'.txt'))
		
		pro = os.path.dirname(pro)

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
					folder_link=(settings.MEDIA_URL + os.path.join('extracts', extract_path))
				)

		book.save()
		genres = meta['subjects'].lower().split(',')
		for g in genres:
			g_obj = Genre.objects.get_or_create(genre=g)[0]
			book.genres.add(g_obj)
	
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


def view_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    review = ""
    if request.user.is_authenticated():
    	rating_set = Rating.objects.filter(book=book, user=request.user)
    	if len(rating_set) > 0:
    		rating = rating_set[0].rating
    		review = rating_set[0].text
    	else:
    		rating = 0
    		review = ""
    else:
    	rating = 0
    	review = ""

    reviews = Rating.objects.filter(book=book).order_by('-created_at')[:5]
    text_reviews = list()
    if len(reviews) > 0:
    	for r in reviews:
    		if not r.user == request.user and len(r.text.strip()) > 0:
	    		text_reviews.append({
	    			'text': r.text,
	    			'rating': r.rating,
	    			'user': r.user.username,
	    		})

    bdict = book.to_dict()
    bdict['user_rating'] = rating
    bdict['text_reviews'] = text_reviews
    bdict['user_review'] = review

    return JsonResponse(bdict)

def faculty(request):
    books = Book.objects.all()
    return render(request,'faculty.html',{"books":books})


def view_book_html(request, book_id, book_slug):
	book = get_object_or_404(Book, pk=book_id)
	reviews = Rating.objects.filter(book=book).order_by('-created_at')[:5]
	text_reviews = list()
	if len(reviews) > 0:
		for r in reviews:
			if not r.user == request.user and len(r.text.strip()) > 0:
				text_reviews.append({
					'text': r.text,
					'rating': r.rating,
					'user': r.user.username,
				})

	return render(request, 'book.html', {
	'id': book_id,
	'book_name': ' '.join(book_slug.split('-')).title(),
	'text_reviews': text_reviews
	})


def read_book(request, book_id):
	book = get_object_or_404(Book, pk=book_id)

	context = {
		'book_dir': book.folder_link,
		'book_title': book.title,
	}
	
	return render(request, 'read.html', context)

@csrf_exempt
def update_ratings(request):
	if request.method == 'POST':
		new_rating = int(request.POST['rating'])
		rating_text = request.POST['text']

		book_id = request.POST['book_id']
		book = Book.objects.get(id=book_id)
		rating_set = Rating.objects.filter(book=book, user=request.user)

		if len(rating_set) > 0:
			rating = rating_set[0]
			book_rating = book.update_ratings(new_rating, rating.rating)
			rating.rating = new_rating
			old_text = rating.text
			rating.text = rating_text.strip()

			new_len = len(rating_text.strip())
			old_len = len(old_text.strip())
			if new_len == 0 and old_len > 0:
				book.text_rating_count -= 1
			elif new_len > 0 and old_len == 0:
				book.text_rating_count += 1

			book.save()
			rating.save()
			
		else:
			rating = Rating(book=book, user=request.user, rating=new_rating, 
							text=rating_text)
			book_rating = book.update_ratings(new_rating)

			if len(rating.text.strip()) > 0:
				book.text_rating_count += 1
				book.save()

			rating.save()

		return JsonResponse({
				'success': True,
				'data': {
					'book_rating': book_rating 
				}
			})
	else:
		return JsonResponse({
				'success': False
			})

@csrf_exempt
def add_read_book(request):
	if request.user.is_authenticated() and request.method == 'POST':
		book_id = request.POST['book_id']
		user = get_object_or_404(UserProfile, user=request.user)
		book = get_object_or_404(Book, pk=book_id)
		user.read_books.add(book)
		user.save()
		return redirect(reverse('read-book', args=(book_id)))
	else:
		return JsonResponse({'success': 'false'})

def contact(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            return redirect(home)
        else:
            return render(request, 'contact.html', {})
            
    elif request.method == 'POST':
        surname = request.POST['nom']
        email = request.POST['email']
        company = request.POST['society']
        function = request.POST['fonction']
        subject = request.POST['sujet']
        message = request.POST['message']
        city = request.POST['ville']
        companyaddress = request.POST['adresse']
        postcode=request.POST['postal']
        phone=request.POST['phone']
        name=request.POST['prenom']

        Contact = ContactForm(surname=surname,
                            email=email,function=function,Postcode=postcode,
                            Company=company,CompanyAddress=companyaddress,
                            Phone=phone,city=city,subject=subject,Message=message,name=name
                             )
        Contact.save()

        return redirect(reverse('home'))


def about(request):
    return render(request, 'about.html', {})

# Authentication --------------------------------------------------------------
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





