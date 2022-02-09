function foldSideBar() {
	if ($('#sidecontent').is(':visible')) {
		$('#sidecontent').toggle();
	    $('.wrapper aside').css({
	    	"width": "20px",
	    	"height": "20px",
	   		"border-radius": "10px",
	    });
	    $('#foldpng').css({
	    	"transform": "rotateX(180deg)",
	    	"top": "15%",
	    	"right": "15%",
	    })
	}
	else {
		$('#sidecontent').toggle();
		$('.wrapper aside').css({
	    	"width": "270px",
	    	"height": "auto",
	    	"border-radius": "30px 15px",
	    });
	    $('#foldpng').css({
	    	"transform": "rotateX(0deg)",
	    	"top": "5%",
	    	"right": "5%",
	    })
	}
}