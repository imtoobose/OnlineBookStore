var book_id = document.getElementById('get-id').value

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

qwest.get('/get-book/' + book_id + '/')
	.then(function(xhr, res){
		loadImage(res['image_link'])
		loadGraph(res['graph_data'])
		setDetails(res)
})