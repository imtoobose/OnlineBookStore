function createImage(src){
	var img, Img
	img = document.createElement('img')
	// document.body.appendChild(img)
	Img = new Image()
	Img.onload = function(){
		console.log('dsadasdas')
		img.src = this.src
	}
	Img.src = src
	return img
}

function add_elements(arr){
	var photos = document.getElementById('photos')
	var arrLen = arr.length, img, a
	for(var i = 0; i < arrLen; i++){
		console.log(arr[i])
		book = arr[i]
		img = createImage(book['image_link'])
		a = document.createElement('a')
		a.href = book['url']
		a.appendChild(img)
		photos.appendChild(a)
	}
}

qwest.get('/get-all-books/')
	.then(function(xhr, res){
		add_elements(res.data)
})
	.catch(function(e, xhr, res){
		console.log(e)
	})