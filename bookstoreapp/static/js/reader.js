document.onreadystatechange = function(){
	if(document.readyState == 'complete'){
		
	}
}

var url = document.getElementById('book-dir').value;
var Book = ePub(url);
console.log(Book)

Book.renderTo("area");	

$("#next").on('click', function(e){
		Book.nextPage();
})

$('#prev').on('click', function(){
	Book.prevPage();
})

EPUBJS.Hooks.register("beforeChapterDisplay").pageTurns = function (callback, renderer) {
    var lock = false;
    console.log('ehy')
    var arrowKeys = function (e) {
        e.preventDefault();
        if (lock) return;

        if (e.keyCode == 37) {
            Book.prevPage();
            lock = true;
            setTimeout(function () {
                lock = false;
            }, 100);
            return false;
        }

        if (e.keyCode == 39) {
            Book.nextPage();
            lock = true;
            setTimeout(function () {
                lock = false;
            }, 100);
            return false;
        }

    };
    renderer.doc.addEventListener('keydown', arrowKeys, false);
    if (callback) callback();
}
