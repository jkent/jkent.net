if (window.location.hash && window.location.hash == '#_=_') {
	if (window.history && history.pushState) {
			window.history.pushState("", document.title, window.location.pathname);
	} else {
			var scroll = {
					top: document.body.scrollTop,
					left: document.body.scrollLeft
			};
			window.location.hash = '';
			document.body.scrollTop = scroll.top;
			document.body.scrollLeft = scroll.left;
	}
}

$(() => {
	$('#header .hamburger').click(function(){
		$('#header .menu').toggleClass('visible');
	});

	const mq = window.matchMedia("(min-width: 650px)");
	mq.addListener(function(mq){
		if (mq.matches){
			$('#header .menu').removeClass('visible');
		}
	});
});

$(document).mouseup(function(e){
	var menu = $("#header .menu");
	var hamburger = $("#header .hamburger");
	if (!hamburger.is(e.target) && hamburger.has(e.target).length === 0 && !menu.is(e.target) && menu.has(e.target).length === 0) {
		menu.removeClass('visible');
	}
});