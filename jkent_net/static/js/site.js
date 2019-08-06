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
	constructor(container, num_links, change) {
		this.container = container;
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
			hash.set('pg', t.first());
			window.location.hash = '#' + hash;
			return false;
		}));
		fragment.append($('<a href="#">&lt;</a>').on('click', () => {
			var hash = new URLSearchParams(window.location.hash.substr(1));
			hash.set('pg', t.prev());
			window.location.hash = '#' + hash;
			return false;
		}));
		for (let i = range.lb; i < range.ub; i++) {
			var link = $('<a href="#">' + i + '</a>');
			link.toggleClass('active', i == this.page_num);
			fragment.append(link.on('click', () => {
				var hash = new URLSearchParams(window.location.hash.substr(1));
				hash.set('pg', i);
				window.location.hash = '#' + hash;
				return false;
			}));
		}
		fragment.append($('<a href="#">&gt;</a>').on('click', () => {
			var hash = new URLSearchParams(window.location.hash.substr(1));
			hash.set('pg', t.next());
			window.location.hash = '#' + hash;
			return false;
		}));
		fragment.append($('<a href="#">&raquo;</a>').on('click', () => {
			var hash = new URLSearchParams(window.location.hash.substr(1));
			hash.set('pg', t.last());
			window.location.hash = '#' + hash;
			return false;
		}));
		return fragment;
	}
	_update() {
		if (this.num_pages <= 1) {
			this.container.empty();
			return;
		}
		var range = this._range();
		this.container.html(this._emit_fragment(range));
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

function index_init(endpoint, validator, text_fn) {
	var index_filter = $('#index_filter');
	var index_new = $('#index_new');
	var typing_timeout = null;
	var typing = false;

	$(window).on('load', load_data);
	$(window).on('hashchange', load_data);
	var pager = new Pager($('.pager'), 10, () => {
		load_data();
		typing = false;
	});

	index_filter.on('keyup', (e) => {
		if (e.keyCode == 27) {
			index_filter.val('');
		}
		if (typing_timeout) {
			clearTimeout(typing_timeout);
			typing_timeout = null;
		}
		typing_timeout = setTimeout(() => {
			var hash = new URLSearchParams(window.location.hash.substr(1));
			hash.delete('pg');
			hash.set('q', index_filter.val());
			var url = new URL(window.location);
			url.hash = '#' + hash;
			if (typing) {
				window.location.replace(url);
			} else {
				typing = true;
				window.location.assign(url);
			}
		}, 250);
	});

	index_new.closest('form').on('submit', (e) => {
		if (!validator(index_new)) {
			return false;
		}
	});

	function load_data() {
		var hash = new URLSearchParams(window.location.hash.substr(1));
		var page_num = hash.get('pg') || 1;
		var query = hash.get('q') || '';

		index_filter.val(query);

		var json_url = new URL(window.location);
		json_url.pathname = endpoint + '/json';
		var search = json_url.searchParams;
		search.set('pg', page_num);
		search.set('q', query)
	
		var index_data = $('.index_data');
		$.get(json_url, (data) => {
			index_data.empty();
			pager.set_pages(data.num_pages)
			for (let entry of data.entries) {
				var html = '<div class="paged-entry">';
				html += '<span><i class="fas fa-trash"></i></span>';
				html += '<a href="#"></a>';
				html += '</div>';
				html = $(html);

				let url = new URL(window.location);
				url.pathname = endpoint + '/' + entry.id;
				url.search = '';
				url.hash = '';

				var a = html.find('a');
				a.text(text_fn(entry));
				a.on('click', () => {
					window.location.assign(url);
					return false;
				});

				var trash = html.find('.fa-trash');
				trash.on('click', () => {
					if (confirm('Delete ' + text_fn(entry) + '?')) {
						$.post(url, {'action': 'delete'}, (data) => {
							load_data();
						});
						return false;
					}
				});

				index_data.append(html);
			}
			pager.goto(page_num);
		});
	}
}

class Subtree {
	constructor(type, mode, is_draft, version, title) {
		this.type = type;
		this.mode = mode;
		this.is_draft = is_draft;
		this.version = version;
		this.title = title;

		this.url = new URL(window.location);
		this.url.search = '';

		this.title_h1 = $('#content > h1');
		this.source_textarea = $('textarea.source');
		this.draft_btn = $('#actionbar a.draft');
		this.raw_btn = $('#actionbar a.raw');
		this.edit_btn = $('#actionbar a.edit');
		this.commit_btn = $('#actionbar a.commit');
		this.restore_btn = $('#actionbar a.restore');
		this.create_btn = $('.subtree .create');
		this.type_sel = $('.subtree .type');

		if (this.mode == 'edit') {
			this.source_last = this.source_textarea.val();
			this.dmp = new diff_match_patch();
			this.title_h1.prop('contentEditable', true);
			this.title_h1.addClass('editable');
		}

		this.raw_btn.on('click', () => {
			this.save(() => {
				var search = new URLSearchParams();
				if (this.mode != 'raw') {
					search.set('raw', '1');
				}
				this.url.search = search;
				window.location = this.url;
			});
			return false;
		});

		this.edit_btn.on('click', () => {
			this.save(() => {
				var search = new URLSearchParams();
				if (this.mode != 'edit') {
					search.set('edit', '1');
				}
				this.url.search = search;
				window.location = this.url;
			});
			return false;
		});

		this.draft_btn.on('click', () => {
			this.save(() => {
				var parsed = this.parse_pathname(this.url.pathname);
				var version = null;
				if (parsed.version == null) {
					version = 'HEAD';
				}
				this.url.pathname = this.build_pathname(parsed.page, version, parsed.path);
				window.location = this.url;
			});
			return false;
		});
	
		if (this.mode == 'raw') {
			this.source_textarea.prop('readonly', true);
		}
		
		this.commit_btn.on('click', () => {
			$.post(this.url, {
				action: 'commit',
			}, (data) => {
				window.location.reload();
			});
			return false;
		});

		if (this.mode == 'raw' || this.mode == 'edit') {
			this.source_resize();
		}
		this.source_textarea.on('input', (event) => {
			this.source_resize();
			this.delayed_save();
		});

		this.title_h1.on('paste', () => {
			this.delayed_save()
		}).on('keypress', (e) => {
			if (e.which == 13) {
				this.title_h1.blur();
				this.save();
				return false;
			}
			this.delayed_save();
			return true;
		});

		this.restore_btn.on('click', () => {
			if (!confirm('Are you sure you want to restore this version?')) {
				return false;
			}
	
			$.post(this.url, {
				action: 'restore',
			}, (data) => {
				var parsed = this.parse_pathname(this.url.pathname);
				this.url.pathname = this.build_pathname(parsed.page, null, parsed.path);
				window.location = this.url;
			});

			return false;
		});

		this.create_btn.on('click', () => {
			$.post(this.url, {
				action: 'create',
				type: this.type_sel.val(),
			}, () => {
				var search = new URLSearchParams();
				search.set('edit', '1');
				this.url.search = search;
				window.location = this.url;
			});
		});
	}
	parse_pathname(pathname) {
		var match = pathname.match(/^\/(\w+)(?:\/_(\w+))?(?:\/(\w+))?/);
		return {
			page: match[0],
			version: match[1],
			path: match[2],
		};
	}
	build_pathname(name, version, path) {
		var pathname = name;
		if (version) {
			pathname += '/_' + version;
		}
		if (path) {
			pathname += '/' + path;
		}
		return pathname;
	}
	save(complete) {
		clearTimeout(this.save_timeout);
		this.save_timeout = null;

		if (this.mode != 'edit') {
			if (typeof complete == 'function') {
				complete();
			}
			return;
		}

		var source_text = this.source_textarea.val();
		var title_text = this.title_h1.text();

		if (source_text == this.source_last && this.title == title_text) {
			if (typeof complete == 'function') {
				complete();
			}
			return;
		}

		var patch = this.dmp.patch_make(this.source_last, source_text);
		var patch_text = this.dmp.patch_toText(patch);
		var post_data = {
			action: 'patch',
			patch: patch_text,
		};
		if (this.title != title_text) {
			this.title = title_text;
			if (this.title == '') {
				this.title = 'Untitled';
				this.title_h1.text(this.title);
			}
			post_data.title = this.title;
			$('title').text(this.title + ' - jkent.net');
		}
		$.post(this.url, post_data, (data) => {
			this.source_last = source_text;
			this.is_draft = data.is_draft;
			this.commit_btn.toggleClass('hidden', !this.is_draft);
			if (typeof complete == 'function') {
				complete();
			}
		});
	}
	source_resize() {
		this.source_textarea.height('inherit');
		var scroll_height = this.source_textarea.prop('scrollHeight');
		var height = parseInt(this.source_textarea.css('border-top-width'), 10)
				   - parseInt(this.source_textarea.css('padding-top'), 10)
				   + scroll_height
				   - parseInt(this.source_textarea.css('padding-bottom'), 10)
				   + parseInt(this.source_textarea.css('border-bottom-width'), 10);
		this.source_textarea.height(height + 'px');

		if (this.source_textarea.prop('clientWidth') < this.source_textarea.prop('scrollWidth')) {
			var num_lines = this.source_textarea.val().split('\n').length;
			height += scroll_height / num_lines;
			this.source_textarea.height(height + 'px');
		}
	}
	delayed_save() {
		clearTimeout(this.save_timeout);
		this.save_timeout = setTimeout(() => this.save(), 500);
	}
}

$(() => {
	window.addEventListener('dragover', (e) => {
		e.preventDefault();
		e.dataTransfer.dropEffect = 'none';
	});
	window.addEventListener('drop', (e) => {
		e.preventDefault();
	});
});

class Treeview {
	constructor(options) {
		Treeview.defaults = {
			can_collapse: true,
			can_collapse_root: false,
			collapsed: false,
			collapsed_root: false,
			draggable: false,
			droppable: false,
			folders_first: true,
			file_drop: false,
			foreign_drop: false,
			multiselect: true,
			only_folders: false,
			root_folder: null,
		};
		this.options = $.extend({}, Treeview.defaults, options);
		this.id = Treeview.counter++;
		this.html = $('<div class="treeview">');
		this.html.css('user-select', 'none');
		this.empty();
		this.path = '';
	}
	_set_node_handlers(node) {
		if (this.options.draggable && node.path != '') {
			node.$li.attr('draggable', true);
		}
		node.$li.on('mousedown', ((e) => {
			e.stopPropagation();
			if (e.ctrlKey || !node.$li.is('.selected')) {
				this.select(node.path, e.shiftKey, e.ctrlKey);
				this._check_selection();
			}
		}).bind(this));
		node.$li.on('click', ((e) => {
			e.stopPropagation();
			if (!e.ctrlKey) {
				this.select(node.path, e.shiftKey, e.ctrlKey);
				this._check_selection();
			}
		}).bind(this));
		node.$li.on('dblclick', ((e) => {
			e.stopPropagation();
			if (node.path == '' || node.path.endsWith('/')) {
				if (!this.options.can_collapse) {
					return;
				}
				if (node.path == '' && !this.options.can_collapse_root) {
					return;
				}
				let visible = node.$ul.is(':visible');
				if (visible) {
					node.$ul.slideUp(200);
				} else {
					node.$ul.slideDown(200);
				}
			} else {
				if (this.dblclick_handler) {
					this.dblclick_handler(node.path, e.shiftKey);
				}
			}
		}).bind(this));
		node.$li.on('dragstart', ((e) => {
			e.stopPropagation();
			Treeview.$drag_ghost = $('<div class="drag-ghost treeview">');
			let $ul = $('<ul class="fa-ul">');
			Treeview.$drag_ghost.append($ul);
			let selection = this.get_selected();
			for (let path of selection) {
				let node = this.find(path);
				let $li = node.$li.clone();
				$li.find('ul').remove();
				$ul.append($li);
			}
			Treeview.$drag_ghost.css('position', 'absolute');
			Treeview.$drag_ghost.css('top', '-150px');
			$(document.body).append(Treeview.$drag_ghost);
			e.originalEvent.dataTransfer.setDragImage(Treeview.$drag_ghost[0], 0, 0);
			e.originalEvent.dataTransfer.setData('text', node.path);
			Treeview.drag_tree = this;
			Treeview.drag_node = node;
		}).bind(this));
		node.$li.on('dragend', ((e) => {
			e.stopPropagation();
			Treeview.$drag_ghost.remove();
			Treeview.$drag_ghost = null;
			Treeview.drag_tree = null;
			Treeview.drag_node = null;
		}).bind(this));
		node.$li.on('dragover', ((e) => {
			if (!this.options.droppable) {
				return;
			}
			e.stopPropagation();
			e.preventDefault();
			e.originalEvent.dataTransfer.dropEffect = 'none';
			do {
				if (!node.path.endsWith('/') && node.path != '') {
					break;
				}
				if (Treeview.drag_node) {
					if (Treeview.drag_tree == this) {
						if (node.path.startsWith(Treeview.drag_node.path)) {
							break;
						}
						if (node.path == Treeview.drag_node.parent.path) {
							break;
						}
					} else if (!this.options.foreign_drop) {
						break;
					}
					e.originalEvent.dataTransfer.dropEffect =
						e.shiftKey ? 'copy' : 'move';
				} else if (this.options.file_drop) {
					e.originalEvent.dataTransfer.dropEffect = 'copy';
				}
			} while(false);

			if (e.originalEvent.dataTransfer.dropEffect != 'none') {
				var $icon = node.$li.find('>i');
				$icon.removeClass('fa-folder').addClass('fa-folder-open');
			}
		}).bind(this));
		node.$li.on('dragleave', ((e) => {
			e.stopPropagation();
			e.preventDefault();
			var $icon = node.$li.find('>i');
			if ($icon.is('.fa-folder-open')) {
				$icon.removeClass('fa-folder-open').addClass('fa-folder');
			}
		}).bind(this));
		node.$li.on('drop', ((e) => {
			if (!this.options.droppable) {
				return;
			}
			e.stopPropagation();
			e.preventDefault();
			var $icon = node.$li.find('>i');
			if ($icon.is('.fa-folder-open')) {
				$icon.removeClass('fa-folder-open').addClass('fa-folder');
			}
			if (!node.path.endsWith('/') && node.path != '') {
				return;
			}
			if (Treeview.drag_node) {
				if (Treeview.drag_tree == this) {
					if (node.path.startsWith(Treeview.drag_node.path)) {
						return;
					}
					if (node.path == Treeview.drag_node.parent.path) {
						return;
					}
				} else if (!this.options.foreign_drop) {
					return;
				}
				if (this.drop_handler) {
					let data = {
						source_node: Treeview.drag_node,
						dest_node: node,
						source_tree: Treeview.drag_tree,
						dest_tree: this,
						shift: e.shiftKey,
					};
					if (Treeview.drag_tree == this) {
						data.type = 'local';
					} else {
						data.type = 'foreign';
					}
					this.drop_handler(data);
				}
			} else if (this.options.file_drop && this.drop_handler) {
				let data = {
					type: 'file',
					source_files: e.originalEvent.dataTransfer.files,
					dest_node: node,
					dest_tree: this,
					shift: e.shiftKey,
				};
				this.drop_handler(data);
			}
		}).bind(this));
	}
	_check_selection() {
		let selection = this.get_selected();
		if (this.select_handler && JSON.stringify(this.selection) !==
				JSON.stringify(selection)) {
			this.select_handler(selection);
			this.selection = selection;
		}
	}
	empty() {
		this.$ul = $('<ul class="fa-ul">');
		this.html.html(this.$ul);
		this.node = {
			children: [],
			path: '',
			parent: this,
		};
		this.root = this;
		this.children = this.node.children;

		if (this.options.root_folder) {
			this.node.name = this.options.root_folder;
			this.node.$li = $('<li class="folder">');
			this.$ul.append(this.node.$li);
			let $icon = $('<i class="fa-li fas fa-folder">');
			let $label = $('<span>').text(this.options.root_folder);
			this.node.$ul = $('<ul class="fa-ul">');
			this.node.$li.append($icon, $label, this.node.$ul);
			if (this.options.collapsed_root) {
				this.node.$ul.css('display', 'none');
			}
			this.root = this.node;
			this.children = [this.node];
			this._set_node_handlers(this.node);
		}
	}
	insert(path, prefix='') {
		if (Array.isArray(path)) {
			for (let i = 0; i < path.length; i++) {
				this.insert(path[i], prefix);
			}
			return;
		}
		path = prefix + path;
		if (path == '') {
			return;
		}
		let matches = path.match(/[^\/]+\/?/g);
		let stack = [this.root];
		for (let depth = 0; depth < matches.length; depth++) {
			let part = matches[depth];
			let dir = false;
			let found = false;
			if (part.endsWith('/')) {
				dir = true;
				part = part.slice(0, -1);
			}
			let i;
			for (i = 0; i < stack[depth].children.length; i++) {
				let node = stack[depth].children[i];
				if (node.name == part) {
					stack.push(node);
					found = true;
					break;
				} else if (this.options.folders_first) {
					let compare_node =
						node.children ? ' ' + node.name : node.name;
					let compare_part = dir ? ' ' + part : part;
					if (compare_node > compare_part) {
						break;
					}
				} else if (node.name > part) {
					break;
				}
			}
			if (found) {
				continue;
			}
			if (!dir && this.options.only_folders) {
				continue;
			}
			let node = {
				name: part,
				parent: stack[depth],
			}
			if (dir) {
				node.children = [];
			}
			if (depth == 0) {
				node.path = node.name;
			} else {
				node.path = stack[depth].path + node.name;
			}
			node.$li = $('<li>');
			let $icon = $('<i class="fa-li fas">');
			let $label = $('<span>').text(part);
			if (dir) {
				node.path += '/';
				node.$li.addClass('folder');
				$icon.addClass('fa-folder');
				node.$ul = $('<ul class="fa-ul">');
				node.$li.append($icon, $label, node.$ul);
				if (this.options.collapsed) {
					node.$ul.css('display', 'none');
				}
			} else {
				node.$li.addClass('file');
				$icon.addClass('fa-file');
				node.$li.append($icon, $label);
			}
			this._set_node_handlers(node);
			let $ul = stack[depth].$ul;
			if (i == 0) {
				$ul.prepend(node.$li);
			} else {
				$ul.find('>li:nth-child(' + i + ')').after(node.$li);
			}
			stack[depth].children.splice(i, 0, node);
			stack.push(node);
		}
	}
	find(path) {
		if (path == '') {
			return this.node;
		}
		let matches = path.match(/[^\/]+\/?/g);
		let stack = [this.root];
		for (let depth = 0; depth < matches.length; depth++) {
			let part = matches[depth];			
			if (part.endsWith('/')) {
				part = part.slice(0, -1);
			}
			for (let i = 0; i < stack[depth].children.length; i++) {
				let node = stack[depth].children[i];
				if (node.name == part) {
					if (stack.length < matches.length) {
						stack.push(node);
						break;
					}
					return node;
				}
			}
		}
		return null;
	}
	remove(node) {
		if (typeof node == 'string') {
			node = this.find(node);
		}
		if (!node) {
			return;
		}
		node.$li.remove();
		node.parent.children.splice(node.parent.children.indexOf(node), 1);
	}
	clear_selection() {
		function _clear_selection(data) {
			for (let i = 0; i < data.length; i++) {
				let node = data[i];
				node.$li.removeClass('selected');
				if (node.children) {
					_clear_selection(node.children);
				}
			}
		}
		_clear_selection(this.children);
	}
	select(node, shift, ctrl) {
		if (typeof node == 'string') {
			node = this.find(node);
		}
		if (this.options.multiselect && shift) {
			this.clear_selection();
			if (this.last_selected
					&& node.parent.children.includes(this.last_selected)) {
				let first = node.parent.children.indexOf(this.last_selected);
				let last = node.parent.children.indexOf(node);
				if (last < first) {
					[first, last] = [last, first];
				}
				for (let i = first; i <= last; i++) {
					node.parent.children[i].$li.addClass('selected');
				}
			} else {
				this.last_selected = node;
				node.$li.addClass('selected');
			}
		} else if (this.options.multiselect && ctrl) {
			let selected = node.$li.is('.selected');
			this.clear_selection();
			node.$li.toggleClass('selected', !selected);
			this.last_selected = node;
		} else if (!this.options.multiselect && ctrl) {
			if (!node.parent.children.includes(this.last_selected)) {
				this.clear_selection();
			}
			node.$li.toggleClass('selected');
			this.last_selected = node;
		} else {
			this.clear_selection();
			node.$li.addClass('selected');
			this.last_selected = node;
		}
	}
	get_selected() {
		function _get_selected(data) {
			let selected = [];
			for (let i = 0; i < data.length; i++) {
				let node = data[i];
				if (node.$li.is('.selected')) {
					selected.push(node.path);
				}
				if (node.children) {
					selected = selected.concat(_get_selected(node.children));
				}
			}
			return selected;
		}
		return _get_selected(this.children);
	}
	list(root) {
		if (typeof root == 'string') {
			root = this.find(root);
		}
		let paths = [];
		function _list(data) {
			if (data) {
				for (let i = 0; i < data.length; i++) {
					let node = data[i];
					paths.push(node.path.slice(root.parent.path.length));
					_list(node.children);
				}
			}
		}
		_list([root]);
		return paths;
	}
	clone(options) {
		options = $.extend({}, this.options, options);
		let treeview = new Treeview(options);
		treeview.insert(this.list());
		return treeview;
	}
}
Treeview.counter = 0;