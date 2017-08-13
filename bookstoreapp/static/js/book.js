var book_id = document.getElementById('get-id').value

function loadImage(src){
	var bookcard = document.getElementById('book-card')
	bookcard.style.backgroundImage = 'url("'+ src  + '")'
}

function loadGraph(grapharr){

}

function setDetails(res){
	document.getElementById('book-title').innerText = res['title']
	document.getElementById('book-description').innerHTML += res['description']
	document.getElementById('book-author').innerText = res['author']
}

qwest.get('/get-book/' + book_id + '/')
	.then(function(xhr, res){
		console.log(res)

		loadImage(res['image_link'])
		// console.log(JSON.parse(res['graph_data']))
		loadGraph(res['graph_data'])
		setDetails(res)
})