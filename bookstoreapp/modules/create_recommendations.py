from django.contrib.auth.models import User
from math import inf
from ..models import Rating, Book

class Node():
	def __init__(self, book):
		self.book = book
		self.neighbors = list()

	def add_neighbor(self, node, weight):
		self.neighbors.append((node, weight))

	def __str__(self):
		return self.book.title


class Graph():
	def __init__(self, books):
		self.nodes = list()

		for book in books:
			# print('INIT', type(book))
			self.add_node(Node(book))

	def add_node(self, newnode):
		for node in self.nodes:
			# print(type(node), type(node.book))
			w = self.get_weight(node.book, newnode.book)
			node.add_neighbor(newnode, w)
			newnode.add_neighbor(node, w)

		self.nodes.append(newnode)


	def get_weight(self, b1, b2):
		w = 0
		g1, g2 = map(lambda x: x.genre.lower().strip().split(','), (b1, b2))
		a1, a2 = b1.author, b2.author
		l1, l2 = b1.language, b2.language
		t1, t2 = b1.title.lower().split(), b2.title.lower().split()
		d1, d2 = b1.description, b2.description

		w += int(l1.lower() == l2.lower())
		w += int(a1.lower() == a2.lower())

		for i in g1:
			for j in g2:
				w += int(i == j)

		for i in t1:
			for j in t2:
				w += int(i == j)

		if w == 0:
			return inf
		else:
			return 1/w


	def display(self):
		def sort_order(k):
			return k[1]

		for node in self.nodes:
			print(node.book.title)
			n = sorted(node.neighbors, key=sort_order)
			print([x[0].book.title for x in n[:4]])
			print('--------------------------')


	def save(self):
		def sort_order(k):
			return k[1]

		data = list()
		for node in self.nodes:
			n = sorted(node.neighbors, key=sort_order)
			similar = [x[0].book for x in n[:4]]
			print('SAVE', similar)
			node.book.r1, node.book.r2, node.book.r3, node.book.r4 = similar
			node.book.save()

			# print('--------------------------')



def create_book_graph():
	books = [b for b in Book.objects.all()]
	g = Graph(books)
	# g.display()
	g.save()
	