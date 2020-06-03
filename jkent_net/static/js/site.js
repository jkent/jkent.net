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
	window.addEventListener('dragover', e => {
		e.preventDefault();
		e.dataTransfer.dropEffect = 'none';
	});
	window.addEventListener('drop', e => {
		e.preventDefault();
	});
});

class Treeview {
	constructor(options) {
		Treeview.defaults = {
			can_collapse: true,
			can_collapse_root: false,
			collapsed: true,
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
		if (Treeview.counter === undefined) {
			Treeview.counter = 0;
		}
		this.id = Treeview.counter++;
		this.html = $('<div class="treeview">');
		this.html.css('user-select', 'none');
		this.path = '';
		this.selected_paths = [];
		this.$ul = $('<ul class="fa-ul">');
		this.html.html(this.$ul);
		this.node = {
			children: [],
			path: '',
			parent: this,
			tree: this,
			type: 'folder',
		};
		this.root = this;
		this.children = this.node.children;
		this.selected_nodes = [];

		if (this.options.root_folder) {
			this.node.name = this.options.root_folder;
			this.node.$li = $('<li class="folder">');
			this.$ul.append(this.node.$li);
			let $icon = $('<i class="fa-li far fa-folder">');
			let $label = $('<span>').text(this.options.root_folder);
			this.node.$ul = $('<ul class="fa-ul">');
			this.node.$li.append($icon, $label, this.node.$ul);
			if (this.options.collapsed_root) {
				this.node.$ul.css('display', 'none');
			}
			this.root = this.node;
			this.children = [this.node];
			this._set_node_handlers(this.node);
			this._add_empty(this.node);
		}

	}
	_set_node_handlers(node) {
		if (this.options.draggable) {
			node.$li.attr('draggable', true);
		}
		node.$li.on('mousedown', (e => {
			e.stopPropagation();
			if (e.ctrlKey || !node.$li.is('.selected')) {
				this.select(node, e.shiftKey, e.ctrlKey);
			}
		}).bind(this));
		node.$li.on('click', (e => {
			e.stopPropagation();
			if (node == this.last_clicked && node != this.root) {
				this.last_clicked = null;
				if (e.originalEvent.detail == 1) {
					let span = node.$li.find('>span:first-of-type');
					span.prop('contenteditable', true);
					span.attr('tabindex', '-1');
					span.focus();
					span.on('keydown', (e => {
						if (e.keyCode == 13) {
							span.blur();
							span.unbind('keydown');
						} else if (e.keyCode == 27) {
							span.text(node.name);
							span.blur();
							span.unbind('keydown');
						}
					}).bind(this));
				}
			} else {
				this.last_clicked = node;
			}
			if (!e.ctrlKey) {
				this.select(node, e.shiftKey, e.ctrlKey);
			}
		}).bind(this));
		node.$li.on('focusout', (e => {
			e.stopPropagation();
			let span = node.$li.find('>span:first-of-type');
			span.prop('contenteditable', false);
			span.removeAttr('tabindex');
			if (this.rename_handler) {
				let name = span.text().trim();
				if (name != node.name) {
					this.rename_handler(node, span.text().trim());
				}
				span.text(node.name);
			}
			this.last_clicked = null;
		}).bind(this));
		node.$li.on('dblclick', (e => {
			e.stopPropagation();
			let span = node.$li.find('>span:first-of-type');
			if (span.is(':focus')) {
				return;
			}
			if (node.path == '' || node.type == 'folder') {
				if (!this.options.can_collapse) {
					return;
				}
				if (node.path == '' && !this.options.can_collapse_root) {
					return;
				}
				if (node.$ul.is(':visible')) {
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
		node.$li.on('dragstart', (e => {
			e.stopPropagation();
			Treeview.$drag_ghost = $('<div class="drag-ghost treeview">');
			let $ul = $('<ul class="fa-ul">');
			Treeview.$drag_ghost.append($ul);
			let nodes = new Set();
			for (let node of this.selected_nodes) {
				while (node != this.root && node.parent.$li.is('.selected')) {
					node = node.parent;
				}
				nodes.add(node);
			}
			for (let node of nodes) {
				let $li = node.$li.clone();
				$li.find('ul').remove();
				$ul.append($li);
			}
			Treeview.$drag_ghost.css('position', 'absolute');
			Treeview.$drag_ghost.css('top', '-150px');
			$(document.body).append(Treeview.$drag_ghost);
			e.originalEvent.dataTransfer.setDragImage(Treeview.$drag_ghost[0], 0, 0);
			e.originalEvent.dataTransfer.setData('text', node.path);
			Treeview.drag_node = node;
		}).bind(this));
		node.$li.on('dragend', (e => {
			e.stopPropagation();
			if (Treeview.$drag_ghost) {
				Treeview.$drag_ghost.remove();
				Treeview.$drag_ghost = null;
			}
			Treeview.drag_node = null;
		}).bind(this));
		node.$li.on('dragenter dragover', (e => {
			if (!this.options.droppable) {
				return;
			}
			e.stopPropagation();
			e.preventDefault();
			e.originalEvent.dataTransfer.dropEffect = 'none';
			do {
				if (node.type != 'folder') {
					break;
				}
				if (Treeview.drag_node) {
					if (Treeview.drag_node.tree == this) {
						let not_allowed = false;
						for (let parent of Treeview.drag_node.tree.selected_parents) {
							if (node.path.startsWith(parent.path)) {
								not_allowed = true;
								break;
							}
							if (node.path == parent.parent.path) {
								not_allowed = true;
								break;
							}
						}
						if (not_allowed) {
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
				let $icon = node.$li.find('>i');
				$icon.removeClass('fa-folder').addClass('fa-folder-open');
				if (!this.dragover_timeout && node.children
						&& !node.$ul.is(':visible')) {
					this.dragover_timeout =
						setTimeout(() => node.$ul.slideDown(200), 500);
				}
			}
		}).bind(this));
		node.$li.on('dragleave', (e => {
			e.stopPropagation();
			e.preventDefault();
			if (this.dragover_timeout) {
				clearTimeout(this.dragover_timeout);
				this.dragover_timeout = null;
			}
			let $icon = node.$li.find('>i');
			if ($icon.is('.fa-folder-open')) {
				$icon.removeClass('fa-folder-open').addClass('fa-folder');
			}
		}).bind(this));
		node.$li.on('drop', (e => {
			if (!this.options.droppable) {
				return;
			}
			e.stopPropagation();
			e.preventDefault();
			if (this.dragover_timeout) {
				clearTimeout(this.dragover_timeout);
				this.dragover_timeout = null;
			}
			let $icon = node.$li.find('>i');
			if ($icon.is('.fa-folder-open')) {
				$icon.removeClass('fa-folder-open').addClass('fa-folder');
			}
			if (node.type != 'folder') {
				return;
			}
			if (Treeview.drag_node) {
				if (Treeview.drag_node.tree == this) {
					for (let parent of Treeview.drag_node.tree.selected_parents) {
						if (node.path.startsWith(parent.path)) {
							not_allowed = true;
							return;
						}
						if (node.path == parent.parent.path) {
							not_allowed = true;
							return;
						}
					}
				} else if (!this.options.foreign_drop) {
					return;
				}
				if (this.drop_handler) {
					this.drop_handler({
						type: Treeview.drag_node.tree == this ? 'local' : 'foreign',
						source_node: Treeview.drag_node,
						selected_parents: Treeview.drag_node.tree.selected_parents,
						dest_node: node,
						shift: e.shiftKey,
					});
				}
			} else if (this.options.file_drop && this.drop_handler) {
				this.drop_handler({
					type: 'items',
					source_items: e.originalEvent.dataTransfer.items,
					dest_node: node,
					shift: e.shiftKey,
				});
			}
		}).bind(this));
	}
	_check_selection() {
		let paths = [];
		let nodes = [];
		function get_selected(data) {
			for (let i = 0; i < data.length; i++) {
				let node = data[i];
				if (node.$li.is('.selected')) {
					nodes.push(node);
					paths.push(node.path);
				}
				if (node.children) {
					get_selected(node.children);
				}
			}
		}
		get_selected(this.children);

		let parents = new Set();
		for (let node of nodes) {
			while (node != this.root && node.parent.$li.is('.selected')) {
				node = node.parent;
			}
			parents.add(node);
		}
		if (this.select_handler &&
				JSON.stringify(this.selected_paths) !== JSON.stringify(paths)) {
			this.select_handler(nodes);
		}
		this.selected_parents = parents;
		this.selected_nodes = nodes;
		this.selected_paths = paths;
	}
	_add_empty(parent) {
		let node = {
			$li: $('<li>'),
			name: '(empty)',
			parent: parent,
			path: parent.path + ' ',
			type: 'empty',
		}
		let $icon = $('<i class="fa-li fa-fw far">');
		let $label = $('<span>').text(node.name);
		node.$li.addClass('empty');
		node.$li.append($icon, $label);
		this._set_node_handlers(node);
		parent.$ul.prepend(node.$li);
		parent.children.splice(0, 0, node);
	}
	insert(path) {
		if (path == '') {
			return;
		}
		let matches = path.match(/[^\/]+\/?/g);
		let stack = [this.root];
		for (let depth = 0; depth < matches.length; depth++) {
			let part = matches[depth];
			let is_folder = false;
			let found = false;
			if (part.endsWith('/')) {
				is_folder = true;
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
					let compare_part = is_folder ? ' ' + part : part;
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
			if (!is_folder && this.options.only_folders) {
				continue;
			}
			let node = {
				$li: $('<li>'),
				name: part,
				parent: stack[depth],
				tree: this,
			}
			if (is_folder) {
				node.children = [];
			}
			if (depth == 0) {
				node.path = node.name;
			} else {
				node.path = stack[depth].path + node.name;
			}
			let $icon = $('<i class="fa-li fa-fw far">');
			let $label = $('<span>').text(part);
			if (is_folder) {
				node.type = 'folder';
				node.path += '/';
				node.$li.addClass('folder');
				$icon.addClass('fa-folder');
				node.$ul = $('<ul class="fa-ul">');
				node.$li.append($icon, $label, node.$ul);
				if (this.options.collapsed) {
					node.$ul.css('display', 'none');
				}
			} else {
				node.type = 'file';
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
			let children = stack[depth].children;
			if (children.length && children[0].type == 'empty') {
				children[0].$li.remove();
				children.splice(i-1, 1, node);
			} else {
				children.splice(i, 0, node);
			}
			stack.push(node);
		}
		let node = stack[stack.length-1];
		if (node.type == 'folder' && node.children.length == '0') {
			this._add_empty(node);
		}
		this.clear_selection();
		this._check_selection();
		return node;
	}
	find(path) {
		if (path == '') {
			return this.root;
		}
		let parts = path.match(/[^\/]+\/?/g);
		let stack = [this.root];
		for (let depth = 0; depth < parts.length; depth++) {
			let part = parts[depth];
			if (part.endsWith('/')) {
				part = part.slice(0, -1);
			}
			let i;
			for (i = 0; i < stack[depth].children.length; i++) {
				let node = stack[depth].children[i];
				if (node.name == part) {
					if (stack.length == parts.length) {
						return node;
					}
					stack.push(node);
					break;
				}
			}
			if (i == stack[depth].children.length) {
				return null;
			}
		}
		return null;
	}
	remove(root) {
		if (typeof root == 'string') {
			root = this.find(root);
		}
		if (root == this.root) {
			let children = root.children.slice(0);
			for (let node of children) {
				this.remove(node);
			}
			return;
		}
		this.clear_selection();
		this._check_selection();
		root.$li.remove();
		root.parent.children.splice(root.parent.children.indexOf(root), 1);
		if (root.parent.children.length == 0) {
			this._add_empty(root.parent);
		}
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
		if (node.type == 'empty') {
			return;
		}
		if (this.options.multiselect && shift) {
			this.clear_selection();
			if (!this.last_selected) {
				node.$li.addclass('selected');
				this.last_selected = node;
				this._check_selection();
				return;
			}
			let [nodes] = this.list();
			var first = nodes.indexOf(this.last_selected);
			var last = nodes.indexOf(node);
			if (last < first) {
				[first, last] = [last, first];
			}
			for (let i = first; i <= last; i++) {
				nodes[i].$li.addClass('selected');
			}
		} else if (!this.options.multiselect && ctrl) {
			let selected = node.$li.is('.selected');
			this.clear_selection();
			node.$li.toggleClass('selected', !selected);
			this.last_selected = node;
		} else if (this.options.multiselect && ctrl) {
			node.$li.toggleClass('selected');
			this.last_selected = node;
		} else {
			this.clear_selection();
			node.$li.addClass('selected');
			this.last_selected = node;
		}
		do {
			node = node.parent;
			if (!node) {
				break;
			}
			if (!node.$ul.is(':visible')) {
				node.$ul.slideDown(0);
			}
		} while (node != this.root);
		this._check_selection();
	}
	list(root) {
		if (!root) {
			root = this.root;
		}
		if (typeof root == 'string') {
			root = this.find(root);
		}
		let nodes = [];
		let paths = [];
		function _list(data) {
			for (let i = 0; i < data.length; i++) {
				let node = data[i];
				if (node.type != 'empty') {
					nodes.push(node);
					paths.push(node.path.slice(root.parent.path.length));
					if (node.children) {
						_list(node.children);
					}
				}
			}
		}
		_list([root]);
		return [nodes, paths];
	}
	exists(root) {
		return this.find(root) !== null;
	}
	rename(node, name) {
		if (!name) {
			return;
		}
		let found = false;
		for (let sibling of node.parent.children) {
			let sibling_name = sibling.name;
			if (sibling_name.endsWith('/')) {
				sibling_name = sibling_name.slice(0, -1);
			}
			if (sibling_name == name) {
				found = true;
				break;
			}
		}
		if (found) {
			return node.name;
		}
		if (node.type == 'folder' && !name.endsWith('/')) {
			name += '/';
		}
		function copy(tree, node, path) {
			let new_node = tree.insert(path);
			new_node.exists = true;

			if (node.type == 'folder') {
				if (node.$ul.is(':visible')) {
					new_node.$ul.slideDown(0);
				} else {
					new_node.$ul.slideUp(0)
				}
				for (let child of node.children) {
					let new_path = path + '/' + child.name;
					if (child.type == 'folder') {
						new_path += '/';
					}
					copy(tree, child, new_path);
				}
			}
		}
		copy(this, node, node.parent.path + name);
		this.remove(node);
	}
}

class TreeviewUpload {
    constructor(file, root, parent) {
        if (TreeviewUpload.active === undefined) {
            TreeviewUpload.active = 0;
            TreeviewUpload.queue = [];
        }

        this.file = file;
        this.root = root;
        this.parent = parent;
		this.node = parent.tree.insert(this.root + file.name);
		this.parent.$ul.slideDown(200);

        if (this.node.$li.has('.progress').length) {
            return;
        };

		this.$progress = $('<span class="progress">');
		this.$buttons = $('<span class="buttons">');
		this.$cancel_btn = $('<a href="#"><i class="fas fa-times"></i></a>');
		this.$cancel_btn.on('click', (() => {
			this.cancel();
		}).bind(this));
		this.$buttons.append(this.$cancel_btn);
		this.node.$li.find('>span').after(this.$progress, this.$buttons);
		this.progressbar = new ProgressBar.Circle(this.$progress[0], {
            color: '#77f',
            strokeWidth: 16,
            trailWidth: 16,
        });
        this.$progress.addClass('queued');
        this.progressbar.set(0.25);

        if (TreeviewUpload.active < 2) {
            this.start()
        } else {
            TreeviewUpload.queue.push(this);
        }
    }
    start() {
        TreeviewUpload.active += 1;
        this.$progress.removeClass('queued');
        this.progressbar.set(0);
        let url = new URL(window.location);
        let search = new URLSearchParams();
        search.set('action', 'upload');
        url.search = search;
        let fd = new FormData();
        fd.append('dest', this.root);
        fd.append('file', this.file);
        this.upload = $.post({
            url: url,
            data: fd,
            xhr: (() => {
                let xhr = $.ajaxSettings.xhr();
                xhr.upload.onprogress = e => {
                    let percent = e.loaded / e.total;
                    this.progressbar.animate(percent);
                };
                return xhr;
            }).bind(this),
            cache: false,
            contentType: false,
            processData: false,
            success: (json => {
                TreeviewUpload.active -= 1;
				this.$progress.remove();
				this.$buttons.remove();
				this.node.exists = true;
                this.next();
            }).bind(this),
            error: (e => {
                TreeviewUpload.active -= 1;
                this.progressbar.animate(100, {
                    color: '#f00',
				});
				this.$buttons.remove();
				if (!this.node.exists) {
					setTimeout((() => {
						this.parent.tree.remove(this.node);
					}).bind(this), 500);
				}
				this.next();
            }).bind(this),
        });
	}
	cancel() {
		let i = TreeviewUpload.queue.indexOf(this);
		if (i >= 0) {
			TreeviewUpload.queue = TreeviewUpload.queue.slice(i, 1);
		} else if (this.upload) {
			this.upload.abort();
		}
		this.$progress.remove();
		this.$buttons.remove();
		if (!this.node.exists) {
			this.parent.tree.remove(this.node);
		}
	}
	next() {
		let upload;
		if (upload = TreeviewUpload.queue.shift()) {
			upload.start();
		}
	}
}

async function getAllEntries(dataTransferItemList) {
    let entries = [];
    let queue = [];
    for (let i = 0; i < dataTransferItemList.length; i++) {
        queue.push(dataTransferItemList[i].webkitGetAsEntry());
    }
    while (queue.length > 0) {
        let entry = queue.shift();
        entries.push(entry);
        if (entry.isDirectory) {
            queue.push(...await readAllDirectoryEntries(entry.createReader()));
        }
    }
    return entries;
}

async function readAllDirectoryEntries(directoryReader) {
    let entries = [];
    let readEntries = await readEntriesPromise(directoryReader);
    while (readEntries.length > 0) {
        entries.push(...readEntries);
        readEntries = await readEntriesPromise(directoryReader);
    }
    return entries;
}

async function readEntriesPromise(directoryReader) {
    try {
        return await new Promise((resolve, reject) => {
            directoryReader.readEntries(resolve, reject);
        });
    } catch (err) {
        console.log(err);
    }
}

async function getFilePromise(entry) {
    try {
        return await new Promise((resolve, reject) => {
            entry.file(resolve, reject);
        });
    } catch (err) {
        console.log(err);
    }
}

async function ask(title, message) {
    let state = false;
    let canceled = true;
    let defer = $.Deferred();
    let $dialog = $('#ask_dialog');
    $dialog.find('span:nth-of-type(2)').html(message);
    $('#dontask_cb').prop('checked', false);
    let dialog = $dialog.dialog({
        resizable: false,
        title: title,
        height: 'auto',
        width: 400,
        modal: true,
        close: () => {
            defer.resolve([state,
                !canceled && $('#dontask_cb').is(':checked')]);
        },
        buttons: {
            No: () => {
                canceled = false;
                state = false;
                dialog.dialog('close');
            },
            Yes: () => {
                canceled = false;
                state = true;
                dialog.dialog('close');
            },
        },
    });
    return defer.promise();
}

async function alert(title, message) {
    let defer = $.Deferred();
    let $dialog = $('#alert_dialog');
    $dialog.find('span:nth-of-type(2)').html(message);
    let dialog = $dialog.dialog({
        resizable: false,
        title: title,
        height: 'auto',
        width: 400,
        modal: true,
        close: () => defer.resolve(),
        buttons: {
            OK: () => dialog.dialog('close'),
        },
    });
    return defer.promise();
}

class FileTreeview extends Treeview {
	constructor(options) {
		super(options);
	}
	load(complete) {
		let url = new URL(window.location);
		let search = new URLSearchParams();
		search.set('action', 'list');
		url.search = search;
		let tree = this;
		$.get(url, data => {
			for (let path of data.paths) {
				let node = tree.insert(path);
				node.exists = true;
			}
			if (complete) {
				complete();
			}
		});
	}
	drop_handler(data) {
		if (data.type == 'items') {
			async function upload_handler() {
				let entries = await getAllEntries(data.source_items);
				let merge, merge_dontask = false;
				let overwrite, overwrite_dontask = false;

				for (let i = 0; i < entries.length; i++) {
					let entry = entries[i];
					let path = data.dest_node.path + entry.fullPath.slice(1);
					if (entry.isDirectory) {
						path += '/';
					}
					let exists = data.dest_node.tree.exists(path);
					if (exists && entry.isDirectory) {
						if (!merge_dontask) {
							[merge, merge_dontask] = await ask('Merge folders?',
								'The folder <b>' + path + '</b> already exists. '
								+ 'Do you wish to merge?');
						}
						if (!merge) {
							entries = entries.filter(e =>
								!e.fullPath.startsWith(entry.fullPath));
						}
					} else if (entry.isFile) {
						if (exists) {
							if (!overwrite_dontask) {
								[overwrite, overwrite_dontask] = await ask(
									'Overwrite?', 'The file <b>' + path + '</b> '
									+ 'already exists. Overwrite?');
							}
							if (!overwrite) {
								continue;
							}
						}
						let root = path.match(/(.+\/)?[^\/]*/)[1] || '';
						let file = await getFilePromise(entry);
						if (file.size <= MAX_UPLAOAD_SIZE) {
							new TreeviewUpload(file, root, data.dest_node);
						} else {
							await alert('File too big', 'The file <b>'
								+ root + file.name + '</b> is too big and '
								+ 'will not be uploaded.');
						}
					}
				}
			}
			upload_handler();
		} else if (data.type == 'local') {
			let merge = true, merge_dontask = false;
			let overwrite = true, overwrite_dontask = false;

			async function collect_rules(src_nodes, dest_node, move) {
				let found = false;
				let rules = [];
				let rmtree = move;

				for (let src_node of src_nodes) {
					found = false;
					for (let child of dest_node.children) {
						if (src_node.name == child.name) {
							found = true;
							if (src_node.type == 'folder') {
								if (!merge_dontask) {
									[merge, merge_dontask] = await ask('Merge '
										+ 'folders?', 'The folder <b>' + child.path
										+ '</b> already exists. Do you wish to '
										+ 'merge?');
								}
								if (merge) {
									let [subrules, rmtree] =
										await collect_rules(src_node.children,
															child, move);
									rules.push(...subrules);
								} else {
									rmtree = false;
								}
							} else if (src_node.type == 'file') {
								if (!overwrite_dontask) {
									[overwrite, overwrite_dontask] = await ask(
										'Overwrite?', 'The ' + child.type + ' <b>'
										+ child.path + '</b> already exists. '
										+ 'Overwrite?');
								}
								if (overwrite) {
									rules.push({
										'op': move ? 'mv' : 'cp',
										'from': src_node.path,
										'to': child.path,
									});
								} else {
									rmtree = false;
								}
							}
						}
					}
					if (!found) {
						rules.push({
							'op': move ? 'mv' : 'cp',
							'from': src_node.path,
							'to': dest_node.path,
						});
					}
					if (src_node.type == 'folder' && rmtree) {
						rules.push({
							'op': 'rmtree',
							'path': src_node.path,
						});
					}
				}
				return [rules, rmtree];
			}

			async function dnd_handler() {
				let [rules] = await collect_rules(data.selected_parents,
												  data.dest_node, !data.shift);
				let url = new URL(window.location);
				let search = new URLSearchParams();
				search.set('action', 'dnd');
				url.search = search;
				$.post({
					url: url,
					data: JSON.stringify({'rules': rules}),
					contentType: 'application/json',
					success: json => {
						if (!json.success) {
							return;
						}
						for (let rule of rules) {
							if (rule.op == 'cp' || rule.op == 'mv') {
								function copy(from_node, to_path) {
									let dest_node;
									if (from_node.type == 'folder') {
										if (!to_path.endsWith('/')) {
											to_path += '/';
										}
										let node = data.dest_node.tree.insert(to_path);
										node.exists = true;
										for (let child of from_node.children.slice()) {
											copy(child, to_path + child.name);
										}
									} else {
										let node = data.source_node.tree.find(to_path);
										if (node && node.type == 'folder') {
											to_path += from_node.name;
										}
										node = data.dest_node.tree.insert(to_path);
										node.exists = true;
										if (rule.op == 'mv') {
											data.source_node.tree.remove(from_node);
										}
									}
								}
								let from_node = data.source_node.tree.find(rule.from);
								let to_path = rule.to;
								if (from_node.type == 'folder') {
									to_path += from_node.name;
								}
								copy(from_node, to_path);
								data.dest_node.$ul.slideDown(200);
							}
							if (rule.op == 'rmtree') {
								data.source_node.tree.remove(rule.path);
							}
						}
					},
				});
			}
			dnd_handler();
		}
	}
	rename_handler(node, name) {
		let url = new URL(window.location);
		let search = new URLSearchParams();
		search.set('action', 'rename');
		url.search = search;
		$.post({
			url: url,
			data: JSON.stringify({'path': node.path, 'name': name}),
			contentType: 'application/json',
			success: json => {
				node.tree.rename(node, json.name);
			},
		});
	}
}