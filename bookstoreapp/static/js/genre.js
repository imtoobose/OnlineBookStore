var genre = document.getElementById('genre-value').value
var page = 1
var fetching = false

function get_more_books(){
	fetching = true
	$("#progressbar").show()
	qwest.get('/get-genre/' + genre + '/' + page + '/')
		.then(function(xhr, res){
			console.log(res)
			if(res.success == 'true'){
				add_elements(res.data)
				page += 1
				fetching = false
				$("#progressbar").hide()
			}
			else{
				$("#progressbar").hide()
			}
	})
		.catch(function(e, xhr, res){
			console.log(e)

		}) 
}

function getDocHeight() {
    var D = document;
    return Math.max(
        D.body.scrollHeight, D.documentElement.scrollHeight,
        D.body.offsetHeight, D.documentElement.offsetHeight,
        D.body.clientHeight, D.documentElement.clientHeight
    );
}


$(window).scroll(function() {
   if($(window).scrollTop() + $(window).height() == getDocHeight() && !fetching) {
       get_more_books()
   }
});

get_more_books()