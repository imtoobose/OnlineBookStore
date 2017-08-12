from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import HttpResponse

# Create your views here.

def home(req):
	return HttpResponse('home sweet home <br> <a href="upload-book"> Upload here </a> ')


def get_books(req):
	return HttpResponse('all books here')

def upload_book(req):
	if req.method == 'GET':
		return render(req, 'uploadform.html', {})
	elif req.method == 'POST':
		f = req.FILES['book']
		print(type(f))
		return HttpResponse('Uploaded')

def view_book(req, book_id, book_slug):
	return HttpResponse(book_id + book_slug)