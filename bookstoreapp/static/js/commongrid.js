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

function add_elements(arr){
	var photos = document.getElementById('photos')
	var arrLen = arr.length, card
	for(var i = 0; i < arrLen; i++){
		book = arr[i]
		card = createCard(book['image_link'], book['author'], book['title'], book['url'])
		photos.appendChild(card[0])
	}
}
