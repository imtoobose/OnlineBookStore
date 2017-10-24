var book_id = document.getElementById('get-id').value
var user_rating = 0, book_rating = 0, user_review = ''

function loadImage(src){
	var bookcard = document.getElementById('book-card')
	bookcard.style.backgroundImage = 'url("'+ src  + '")'
}

function loadGraph(grapharr){
	grapharr = JSON.parse(grapharr)
	if(grapharr.length == 0){ 
		$("#chapter-graph").remove()
		$('#user-ratings').css({
			"margin-bottom": "15px"
		})
		return
	}

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
			book_id: book_id,
			text: user_review,
		})
		.then(function(xhr, response){
			user_rating = id
			$("#edit-review").show()
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

function updateRatings(rating, review){
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

	$("#review-field").val(user_review)

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

function updateTextReviews(reviews){
	for(var i = 1; i<=reviews.length; i++)
		$("#text-review").append()
}

var dialog = new mdc.dialog.MDCDialog(document.querySelector('#review-dialog'));


if($("#edit-review").length){
	dialog.listen('MDCDialog:accept', function() {
	  console.log('accepted');
	  user_review = $("#review-field").val()
	  qwest.post('/update-ratings/', {
	  	rating: user_rating,
	  	book_id: book_id,
	  	text: user_review,
	  })
	})

	dialog.listen('MDCDialog:cancel', function() {
	  console.log('canceled');
	})

	document.querySelector('#edit-review').addEventListener('click', function (evt) {
	  dialog.lastFocusedTarget = evt.target;
	  dialog.show();
	})
}

$("#add-read-book-button").click(function(){
	qwest.post('/add-read-book/', {
		book_id: book_id
	}).then(function(xhr, res){
		window.location = '/read/' + book_id + '/'
	})
	.catch(function(e, xhr, res){
		console.log(e)
	})
})

qwest.get('/get-book/' + book_id + '/')
	.then(function(xhr, res){
		console.log(res)
		user_rating = Number(res['user_rating'])
		book_rating = Number(res['avg_rating'])
		user_review = res['user_review']
		
		if(user_rating === 0){
			$("#edit-review").hide()
		}

		updateRatings(user_rating, user_review)
		updateBookRatings(book_rating)
		// updateTextReviews(res['text_reviews'])
		loadImage(res['image_link'])
		loadGraph(res['graph_data'])
		setRatingListener()
		setDetails(res)
})