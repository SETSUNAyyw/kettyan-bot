$(window).on('scroll', function() {
	var y = $(this).scrollTop();
	var h = $(this).height();
	$('#totop').toggleClass('slide-in', y > h)
});