from __future__ import division, print_function
import os
import zipfile
from lxml import etree
import sys, getopt
import shutil
import glob
from bs4 import BeautifulSoup
from .OrderedSet import OrderedSet
import pickle

def __get_or_empty__(content_file, tag, ns):
	if content_file.find(tag, ns) is not None:
		return content_file.find(tag, ns).text
	else:
		return ''

def __get_extension__(file_path):
	return os.path.splitext(os.path.basename(file_path))[1]

def __get_file_name__(file_path):
	return os.path.splitext(os.path.basename(file_path))[0]

def convert(input_file, output_file='book.txt', extract_chapters=True, make_meta=True):
	"""Converts input_file (epub) to a text file, optionally creating text files\
		for each individual chapter in the toc.ncx file, and a pickled python array\
		with chapter information in a file 'meta.pkl'

		params:
		input_file -- the input file. Should be a valid epub file
		output_file -- optional path for output .txt file
		extract_chapters -- boolean option for extracting individual chapters. Default: True
		make_meta -- boolean option for making a meta python array pickle file. Default: True

	"""

	if not __get_extension__(input_file) == '.epub':
		raise TypeError('Invalid File Type. File must be a .epub file.')

	i_file_name = __get_file_name__(input_file)

	if output_file == 'book.txt':
		output_file = i_file_name + '.txt'
		output_dir = i_file_name
	else:
		output_dir = os.path.join(os.getcwd(), os.path.dirname(output_file))
		output_file = __get_file_name__(output_file)

	print('Converting ', i_file_name)

	if not os.path.exists(os.path.join(os.getcwd(), 'extracts', i_file_name)):
		f = zipfile.ZipFile(input_file, 'r')
		f.extractall(os.path.join( os.getcwd(), 'extracts', i_file_name))
		f.close()

	book_dir = os.path.join(os.getcwd(), 'extracts', i_file_name)
	meta_dir = os.path.join(book_dir, 'META-INF')

	container_xml = etree.parse(os.path.join(meta_dir, 'container.xml'))
	root = container_xml.getroot()
	root_path = root.find('.//rootfile', root.nsmap).attrib['full-path']

	root_dir = os.path.dirname(root_path)
	root_file = os.path.basename(root_path)

	content_file = etree.parse(os.path.join(book_dir, root_dir, root_file)).getroot()
	content_dir = os.path.join(book_dir, root_dir)

	processed_files_path = os.path.join(os.getcwd(), output_dir)
	if not os.path.exists(processed_files_path):
		os.makedirs(processed_files_path)

	processed = open(os.path.join(processed_files_path, output_file), 'w+')
	chapter_folder = os.path.join(processed_files_path, 'chapters')

	if not os.path.exists(os.path.join(os.getcwd(), output_dir)):
		os.makedirs(os.path.join(os.getcwd(), output_dir))

	if extract_chapters and not os.path.exists(os.path.join(os.getcwd(), output_dir, 'chapters')):
		os.makedirs(os.path.join(output_dir, 'chapters'))
	
	ns = content_file.nsmap

	metadata = content_file.find('metadata', ns)

	ns.update(metadata.nsmap)
	
	title = __get_or_empty__(content_file, './/dc:title', ns)
	author = __get_or_empty__(content_file, './/dc:creator', ns)
	desc = __get_or_empty__(content_file, './/dc:description', ns)
	pub_date = __get_or_empty__(content_file, './/dc:date', ns)
	publication = __get_or_empty__(content_file, './/dc:publisher', ns)
	language = __get_or_empty__(content_file, './/dc:language', ns)

	subarr = content_file.findall('.//dc:subject', ns)
	print(subarr)
	if not subarr == None:
		subjects = ','.join([x.text for x in subarr])
	else:
		subjects = ''

	manifest = content_file.findall('./manifest//', ns)

	meta = {
		'author': author,
		'title': title,
		'description': desc,
		'language': language,
		'pub_date': pub_date,
		'publication':publication,
		'subjects': subjects,
		'chapters': [],
	}

	text_file_paths = []

	search_toc = glob.glob(os.path.join('extracts','**/*.ncx'), recursive=True)

	if len(search_toc) > 0:
		toc_file = search_toc[0]
	else:
		toc_file = None

	cover_file_path = None
	for i in manifest:
		if i.attrib['media-type'] == 'application/xhtml+xml':
			text_file_paths.append(os.path.join(content_dir, i.attrib['href'] ) )
		elif i.attrib['media-type'] == 'image/jpeg' or i.attrib['media-type'] == 'image/png':
			if 'cover' in i.attrib['id']: 
				cover_file_path = i.attrib['href']
				with open(os.path.join(content_dir, cover_file_path), 'rb') as cover_file:
					writer = open(os.path.join(processed_files_path, 'cover' + __get_extension__(cover_file_path)), 'wb+')
					for chunk in cover_file:
						writer.write(chunk)
					writer.close()
					meta['cover'] = 'cover' + __get_extension__(cover_file_path)

	if not 'cover' in meta:
		meta['cover'] = None

	for chap in text_file_paths:
		with open(chap, 'r') as page_file:
			soup = BeautifulSoup(page_file, 'lxml')

			content = ''
			
			for i in soup.body.children:
				try:
					content += i.text + " "
				except:
					continue

			processed.write(content)

			if extract_chapters and not toc_file:
				with open(os.path.join(chapter_folder, __get_file_name__(chap) + '.txt'), 'w+') as chapfile:
					chapfile.write(content)


	if toc_file and extract_chapters:
		filenames = OrderedSet()
		idnames = dict()

		with open(toc_file, 'r') as f:
			soup = BeautifulSoup(f, 'lxml')

		navpoints = soup.find_all('navpoint')

		for navpoint in navpoints:
			content_ptr = os.path.join(os.path.dirname(toc_file), navpoint.content['src'])
			chapter_title = navpoint.navlabel.text.strip()
			play_order = navpoint['playorder']

			if os.path.isfile(content_ptr):
				filenames.add((content_ptr, chapter_title, play_order))

			else:
				filename, contentid = content_ptr.split('#')
				filenames.add((filename, None, None))

				if idnames.__contains__(filename):
					idnames[filename].append((contentid, chapter_title, play_order))
				else:
					idnames[filename] = [(contentid, chapter_title, play_order)]

		lastfile = None

		for f, chapname, play_order in filenames:
			if f in idnames and len(idnames[f]) > 0:
				with open(f, 'r') as file:
					chapsoup = BeautifulSoup(file, 'lxml')
					headers = chapsoup.body.find_all(['h'+str(x) for x in range(1, 7)])

				content = '\n'

				for i in chapsoup.body:
					if i in headers:
						break
					else:
						try:
							content += i.text + ' '
						except:
							continue

				if not lastfile == None:
					with open(lastfile,  'a') as lastf:
						lastf.write(content)

					lastfile = None

				for contentid, chapter_title, play_order in idnames[f]:
					meta['chapters'].append({
						'playorder': play_order,
						'chapname': chapter_title,
						'filename': os.path.join('chapters', play_order + '-' + chapter_title + '.txt'),
					})

					lastfile = os.path.join(chapter_folder, play_order + '-' + chapter_title + '.txt')
					hh = chapsoup.body.find(id=contentid)
					content = ''
					for i in hh.next_siblings:
						if i in headers:
							break
						else:
							try:
								content += i.text + ' '
							except:
								continue

					with open(lastfile, 'w+') as afile:
						afile.write(content)

			else:
				meta['chapters'].append({
					'playorder': play_order,
					'chapname': chapname,
					'filename': os.path.join('chapters', play_order + '-' + chapname + '.txt'),
				})

				with open(f, 'r') as file:
					chapsoup = BeautifulSoup(file, 'lxml')
					content = ''

					for i in chapsoup.body:
						try:
							content += i.text + '\n'
						except:
							continue

					with open(os.path.join(chapter_folder, play_order + '-' + chapname + '.txt'), 'w+') as chapfile:
						chapfile.write(content)

	if make_meta:
		with open(os.path.join(processed_files_path, 'meta.pkl'), 'wb') as metapkl:
			pickle.dump(meta, metapkl)

	processed.close()
	shutil.rmtree('extracts')
	print('Completed conversion to ', os.path.join(processed_files_path, output_file))
	return os.path.join(processed_files_path, output_file)


if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hi:o:e:", [])
	
	except getopt.GetoptError:
		print('Invalid options or arguments')
		sys.exit(2)

	input_file_path = None
	output_file_path = "book.txt"
	extract_chapters = True

	if ('-h', '') in opts:
		print('Epub To Text\n---------------------------\nCommand Line Interface Usage:\n'
			  'python epubtext.py\n-i <input_epub_file>\tInput EPUB file\n-o <output_file_name>\tOutput'
			  '.txt file path (optional)\n-e <True|False>\t\tExtract Text files for each chapter.'
 			  'Default: False\n')

		sys.exit()

	for opt, arg in opts:
		if opt == '-i':
			print('here', arg)
			input_file_path = arg
		elif opt == '-o':
			output_file_path = arg
		elif opt == '-e':
			if arg == 'True':
				extract_chapters = True
			elif arg == 'False':
				extract_chapters = False
			else:
				print('ERROR: Invalid option for extract chapter')
				sys.exit(1)

	if not input_file_path:
		print('ERROR: Input file required')
		sys.exit(1)

	if not __get_extension__(input_file_path) == '.epub':
		print('ERROR: Input file is not in EPUB format')
		sys.exit(1)

	convert(input_file_path, output_file_path, extract_chapters)