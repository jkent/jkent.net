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

class Taglist {
    constructor(selector, input, validate) {
		this._taglist = $(selector);
		this._input = $(input);
        this._entry = this._taglist.find('.input');
		this._validate = validate;
		this._submit = false;

		this._taglist.on('click', () => {
            this._entry.focus();
        }).parent().find('label').on('click', () => {
            this._entry.focus();
        });

        this._taglist.addClass('empty');
        this._entry.prop({
            contenteditable: true,
            spellcheck: false,
        }).on('focus', () => {
            this._taglist.addClass('focus');
            document.execCommand('selectAll', false, null);
        }).on('blur', () => {
            this._taglist.toggleClass('empty', this.tags().length == 0 && this._entry.text().length == 0);
            this._taglist.removeClass('focus');
            this.add_tag(this._entry.text());
            this._entry.text('');
        }).on('keypress', (e) => {
            if (e.keyCode == 13) {
				this._submit = true;
				var text = this._entry.text().trim();
				if (text == '') {
					this._taglist.closest('form').submit();
				} else {
					this.add_tag(text);
				}
				this._entry.text('');
				return false;
			} else if (e.keyCode == 27) {
                this._entry.text('');
            } else if (e.keyCode == 32) {
                this.add_tag(this._entry.text());
                this._entry.text('');
                return false;
            }
        }).on('keydown', (e) => {
            if (e.keyCode == 8) {
                var text = this._entry.text();
                if (text == '') {
                    this.remove_tag(this.tags().pop());
                }
            }
        }).on('paste', (e) => {
            let paste = (event.clipboardData || window.clipboardData).getData('text');
            paste = paste.toLowerCase();
            for (let tag of paste.split(' ')) {
                this.add_tag(tag);
            }
            e.preventDefault();
        });
        this._update();
    }
    _update() {
		var tags = this.tags();
		this._taglist.toggleClass('empty', tags.length == 0 && this._entry.text().length == 0);
		this._taglist.find('.tag').remove();
		for (let tag of tags.reverse()) {
            var span = $('<span/>');
            span = span.addClass('tag').text(tag);
            span = span.append('<i class="fas fa-times"></i>');
            span.prependTo(this._taglist).find('i').on('click', () => {
                this.remove_tag(tag);
                span.remove();
            });
        }
    }
    add_tag(tag, force, submit) {
		tag = tag.trim();
        if (tag == '' || (!force && typeof this._validate == 'function' && !this._validate(tag))) {
			this._submit = false;
			return;
		}
		var tags = this.tags();
		tags.push(tag.toLowerCase());
		tags = [...new Set(tags.sort())];
		this._input.val(tags.join(','));
		this._update();
		if (this._submit) {
			this._taglist.closest('form').submit();
		}
    }
    remove_tag(tag) {
		tag = tag.trim().toLowerCase();
		var tags = this.tags();
		tags.splice(tags.indexOf(tag), 1);
		tags = [...new Set(tags)].sort();
		this._input.val(tags.join(','));
		this._update();
    }
    tags() {
		var tags = this._input.val().split(',').filter(word => /\w/.test(word));
		return [...new Set(tags)].sort();
    }
}