var book_id = document.getElementById('get-id').value
var user_rating = 0, book_rating = 0

function loadImage(src){
	var bookcard = document.getElementById('book-card')
	bookcard.style.backgroundImage = 'url("'+ src  + '")'
}

function loadGraph(grapharr){
	grapharr = JSON.parse(grapharr)
	var arrlen = grapharr.length,
		x = new Array(arrlen),
		y = new Array(arrlen)

	for(var i = 0; i <arrlen; i++){
		x[i] = grapharr[i]['chap']
		y[i] = grapharr[i]['count']
	}

	var ctx = document.getElementById("chapter-graph")
	var config = {
		type: 'line',
		data: {
			datasets: [{
				data: y,
				fill: false,
				borderColor: '#F44336'
			}],
			labels: x,

		},
		options: {
			legend: {
				display: false
			},
			title:{
				display: true,
				text: 'Chapter Wise Analysis of Action',
				fontFamily: 'Roboto, sans-serif',
				fontSize: 16,
			},
			layout: {
				padding:{
					left: 25,
					right: 25,
					top: 25,
					bottom: 25
				}

			},
			scales:{
				yAxes:[{
					scaleLabel: {
						display: true,
						labelString: 'Normalized Verb Count',
					},
					gridLines:{
						display:false,
					}
				}],
				xAxes: [{
					ticks: {
						minRotation: 90,
    					autoSkip: false,
    					fontSize: 8,
					},
					scaleLabel: {
						display: true,
						labelString: 'Chapter',
					},
					gridLines:{
						display:true,
						color: 'rgba(177, 177, 177, 0.1)'
					}
				}]
			}
		}

	}
	var bookChart = new Chart(ctx, config)

}

function setDetails(res){
	document.getElementById('book-title').innerText = res['title']
	document.getElementById('book-description').innerHTML += res['description']
	document.getElementById('book-author').innerText = res['author']
}

function setRatingListener(){
	$('.btn-rating-star').on('click', function(){
		console.log('clicked', this.id)
		var id = Number(this.id.split('-')[0])
		qwest.post('/update-ratings/', {
			rating: id,
			book_id: book_id
		})
		.then(function(xhr, response){
			user_rating = id
			console.log(response.data.book_rating)
		})
	})

	$('.btn-rating-star').hover(function(e){
		var id = e.target.id.split('-')[0]
		updateRatings(id)
	}, function(){
		updateRatings(user_rating)
	})
}

function updateRatings(rating){
	var i = 1, ur = Math.floor(rating)
	for(; i <= 5; i ++){
		if(i<=ur) {
			$('#user-rating-star-' + i)
			.addClass('rating-star-active')
			.removeClass('rating-star-inactive')
		}
		else{
			$('#user-rating-star-' + i)
			.addClass('rating-star-inactive')
			.removeClass('rating-star-active')
		}
	}
}

function updateBookRatings(rating){
	var i = 1, ur = Math.floor(rating)
	for(; i <= 5; i ++){
		if(i<=ur) {
			$('#book-rating-star-' + i)
			.addClass('rating-star-active')
			.removeClass('rating-star-inactive')
		}
		else{
			$('#book-rating-star-' + i)
			.addClass('rating-star-inactive')
			.removeClass('rating-star-active')
		}
	}	
}

qwest.get('/get-book/' + book_id + '/')
	.then(function(xhr, res){
		console.log(res)
		user_rating = Number(res['user_rating'])
		book_rating = Number(res['avg_rating'])
		updateRatings(user_rating)
		updateBookRatings(book_rating)
		loadImage(res['image_link'])
		loadGraph(res['graph_data'])
		setRatingListener()
		setDetails(res)
})