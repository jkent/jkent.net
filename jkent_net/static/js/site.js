$(() => {
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

	$('#header .hamburger').click(function(){
		$('#header .menu').toggleClass('visible');
	});

	const mq = window.matchMedia("(min-width: 650px)");
	mq.addListener(function(mq){
		if (mq.matches){
			$('#header .menu').removeClass('visible');
		}
	});

	$(document).on('mouseup', (e) => {
		var menu = $("#header .menu");
		var hamburger = $("#header .hamburger");
		if (!hamburger.is(e.target) && hamburger.has(e.target).length === 0 && !menu.is(e.target) && menu.has(e.target).length === 0) {
			menu.removeClass('visible');
		}
	});
});

class Pager {
	constructor(selector, num_links, change) {
		this.selector = selector;
		this.num_links = num_links;
		this.num_pages = 1;
		this.page_num = 1;
		this.change = change;
		this._update();
	}
	_range() {
		return {
			lb: Math.max(Math.min(this.num_pages, (this.page_num || 1) + this.num_links / 2) - this.num_links, 0) + 1,
			ub: Math.min(Math.max(0, (this.page_num || 1) - this.num_links / 2) + this.num_links, this.num_pages) + 1,
		};
	}
	_emit_fragment() {
		var range = this._range();
		var t = this;
		var fragment = $('<div/>');
		fragment.append($('<a href="#">&laquo;</a>').on('click', () => {
			var hash = new URLSearchParams(window.location.hash.substr(1));
			hash.set('page', t.first());
			window.location.hash = '#' + hash;
			return false;
		}));
		fragment.append($('<a href="#">&lt;</a>').on('click', () => {
			var hash = new URLSearchParams(window.location.hash.substr(1));
			hash.set('page', t.prev());
			window.location.hash = '#' + hash;
			return false;
		}));
		for (let i = range.lb; i < range.ub; i++) {
			var link = $('<a href="#">' + i + '</a>');
			link.toggleClass('active', i == this.page_num);
			fragment.append(link.on('click', () => {
				var hash = new URLSearchParams(window.location.hash.substr(1));
				hash.set('page', i);
				window.location.hash = '#' + hash;
				return false;
			}));
		}
		fragment.append($('<a href="#">&gt;</a>').on('click', () => {
			var hash = new URLSearchParams(window.location.hash.substr(1));
			hash.set('page', t.next());
			window.location.hash = '#' + hash;
			return false;
		}));
		fragment.append($('<a href="#">&raquo;</a>').on('click', () => {
			var hash = new URLSearchParams(window.location.hash.substr(1));
			hash.set('page', t.last());
			window.location.hash = '#' + hash;
			return false;
		}));
		return fragment;
	}
	_update() {
		var target = $(this.selector);
		if (this.num_pages <= 1) {
			target.empty();
			return;
		}
		var range = this._range();
		target.html(this._emit_fragment(range));
	}
	set_pages(num_pages) {
		this.num_pages = num_pages;
		this.goto(1, true);
	}
	goto(page, forced_update) {
		var next_page = Math.max(1, Math.min(page, this.num_pages));
		if (forced_update || next_page != this.page_num) {
			this.page_num = next_page;
			this._update();
		}
	}
	first() {
		return 1;
	}
	prev() {
		return Math.max(1, this.page_num - 1);
	}
	next() {
		return Math.min(this.page_num + 1, this.num_pages);
	}
	last() {
		return Math.max(this.num_pages, 1);
	}
}