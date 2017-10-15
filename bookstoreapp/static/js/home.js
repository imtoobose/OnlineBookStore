function truncate(s, l){
	if(s.length > l && l>3)
		return s.substring(0, l - 3) + '...' 
	else
		return s
}

function toTitleCase(s){
	return s.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

function createCard(src, auth, title, url){
	var card = document.createElement('a'),
			primary = document.createElement('section'),
				c_title = document.createElement('h3'),
				c_subtitle = document.createElement('h5');		
			action = document.createElement('section')

	card.className += 'mdc-card home-card'
	card.style.backgroundImage = 'url("'+ src  + '")'
	card.href = url
	primary.className += 'mdc-card__primary'
	c_title.className += 'mdc-card__title mdc-card__title--large'
	c_title.innerText = truncate(title, 20)
	c_subtitle.className += 'mdc-card__subtitle'
	c_subtitle.innerText = truncate(auth, 15)
	action.className += ''

	primary.appendChild(c_title)
	primary.appendChild(c_subtitle)

	card.appendChild(primary)

	var regular_card = card.cloneNode(true)
	regular_card.classList += ' regular-card mdc-layout-grid__cell mdc-layout-grid__cell--span-2 mdc-layout-grid__cell--span-4-tablet mdc-layout-grid__cell--span-12-phone'
	var swiper_card = card.cloneNode(true)
	swiper_card.className += ' swiper-slide'
	return [regular_card, swiper_card]
}

function initlializeSlider(){

	var wwidth = window.innerWidth;
	var visibleSlides = 0;
	if(wwidth >= 1185){
		visibleSlides = 10;
	}
	else if(wwidth >= 820){
		visibleSlides = 6;
	}
	else if(wwidth >= 571){
		visibleSlides = 4;
	}
	else if(wwidth >= 375){
		visibleSlides = 3;
	}
	else{
		visibleSlides = 1;
	}

	var next = document.getElementById('swiper-button-next'),
		prev = document.getElementById('swiper-button-prev')  

	var mySwiper = new Swiper('.swiper-container', {
	    speed: 400,
	    spaceBetween: 15,
	    slidesPerView: visibleSlides,
	    nextButton: next,
	    prevButton: prev,
	    slidesOffsetBefore: visibleSlides > 1 ? Math.min(100, wwidth*0.1) : 0,
	    slidesOffsetAfter: visibleSlides > 1 ? Math.min(100, wwidth*0.1) : 0,
	    grabCursor: true,
	    slidesPerGroup: 4,
	    onProgress: function(e){
	        if(e.isBeginning){
	            prev.classList.add('hide')
	        } else if(e.isEnd){
	            next.classList.add('hide')
	        } else {
	            prev.classList.remove('hide')
	            next.classList.remove('hide')
	        }
	    }

	})
}

function add_elements(arr, narr){
	var photos = document.getElementById('photos')
	var slidewrap = document.getElementById('swiper-wrapper')

	var arrLen = arr.length, img, a, card
	for(var i = 0; i < arrLen; i++){
		book = arr[i]
		card = createCard(book['image_link'], book['author'], book['title'], book['url'])
		
		slidewrap.appendChild(card[1])

		book = narr[i]
		card = createCard(book['image_link'], book['author'], book['title'], book['url'])
		photos.appendChild(card[0])
	}
	
	initlializeSlider()
}

function createGrid(g){
	var div, h1, h2, photos 
	div = document.createElement('div')
	h1 = document.createElement('h1')
	h3 = document.createElement('h3')
	photos = document.createElement('div')

	div.classList.add('mdc-layout-grid')
	div.classList.add('photo-grid')
	h1.classList.add('content-title')
	h3.classList.add('content-subtitle')
	photos.classList.add('photos')
	photos.classList.add('mdc-layout-grid__inner')
	h1.innerText = toTitleCase(g.genre)
	h3.innerText = ''
	div.appendChild(h1)
	div.appendChild(h3)
	div.appendChild(photos)
	var book, card, bookarr = g.books

	for(var i  in bookarr){
		book = bookarr[i]
		card = createCard(book['image_link'], book['author'], book['title'], book['url'])[0]
		photos.appendChild(card)
	}

	return div
}

function add_genres(arr){
	console.log('here')
	var genres = document.getElementById('genres')
	var g_len = arr.length
	console.log('here', g_len)
	for(var i = 0; i<g_len; i++){
		g = arr[i]
		grid = createGrid(g)
		console.log(grid)
		genres.appendChild(grid)
	}
}

qwest.get('/get-all-books/')
	.then(function(xhr, res){
		console.log(res)
		add_elements(res.data, res.new_books)
		add_genres(res.genre_books)
})
	.catch(function(e, xhr, res){
		console.log(e)
	}) 