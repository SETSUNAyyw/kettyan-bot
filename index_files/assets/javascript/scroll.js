$(window).on('scroll', function() {
	const re = "#";
	var y = $(this).scrollTop();
	var h = $(this).height();
	var sections = $('#sidecontent').find('a:not([href^="http"])').toArray();
	$('#totop').toggleClass('slide-in', y > h)
	for (var i = 0; i < sections.length; i++) {
		sections[i] = (sections[i].toString().match(/^.*(#.*)/)[1]);
	}
	for (var i = 0; i < sections.length; i++) {
		var prev_h = $(sections[i]).offset().top - 150;
		var next_h;
		if (i == sections.length - 1) {
		 	next_h = $(document).height();
		}
		else {
		 	next_h = $(sections[i + 1]).offset().top - 150;
		}
		var sec = sections[i] + "section";
		if ((y >= prev_h) && (y < next_h)) {
			$(sec).css({
				"border-color": "#2083e0",
			});
		}
		else {
			$(sec).css({
				"border-color": "#eee",
			});
		}
	}
});