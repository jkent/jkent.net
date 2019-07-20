$(() => {
	/* Code for all modes */
	var url = new URL(window.location);
	url.search = '';
	
	var draft_btn = $('#actionbar a.draft');
	var raw_btn = $('#actionbar a.raw');
	var edit_btn = $('#actionbar a.edit');

	function parse_pathname(pathname) {
		match = pathname.match(/^\/(?<page>\w+)(?:\/_(?<version>\w+))?(?:\/(?<path>\w+))?/);
		return match.groups;
	}

	function build_pathname(name, version, path) {
		var pathname = name;
		if (version) {
			pathname += '/_' + version;
		}
		if (path) {
			pathname += '/' + path;
		}
		return pathname;
	}

	/* dummy save function */
	if (subtree.mode == 'render' || subtree.mode == 'raw') {
		function source_save_patch(complete) {
			if (typeof complete == 'function') {
				complete();
			}
		}
	}

	raw_btn.on('click', () => {
		source_save_patch(() => {
			var search = new URLSearchParams();
			if (subtree.mode != 'raw' || subtree.mode == 'edit') {
				search.set('raw', '1');
			}
			url.search = search.toString();
			window.location = url;
		});
		return false;
	});

	edit_btn.on('click', () => {
		source_save_patch(() => {
			var search = new URLSearchParams();
			if (subtree.mode != 'edit' || subtree.mode == 'raw') {
				search.set('edit', '1');
			}
			url.search = search;
			window.location = url;
		});
		return false;
	});

	draft_btn.on('click', () => {
		source_save_patch(() => {
			var parsed = parse_pathname(url.pathname);
			var version = null;
			if (parsed.version == null) {
				version = 'HEAD';
			}
			url.pathname = build_pathname(parsed.page, version, parsed.path);
			window.location = url;
		});
		return false;
	});

	if (subtree.mode == 'render') {
		return;
	}

	/* Code for raw and edit modes */
	var source_textarea = $('#content > textarea.source');
	var commit_btn = $('#actionbar a.commit');

	if (subtree.mode == 'raw') {
		source_textarea.prop('readonly', true);

		commit_btn.on('click', () => {
			if (timeout) {
				clearTimeout(timeout);
				timeout = null;
			}
			$.post(url, {
				action: 'commit',
			}, (data) => {
				window.location = url;
			});
			return false;
		});
	}

	function source_resize() {
		source_textarea.height('inherit');
		var scrollHeight = source_textarea.prop('scrollHeight');
		var height = parseInt(source_textarea.css('border-top-width'), 10)
					- parseInt(source_textarea.css('padding-top'), 10)
					+ scrollHeight
					- parseInt(source_textarea.css('padding-bottom'), 10)
					+ parseInt(source_textarea.css('border-bottom-width'), 10);

		source_textarea.height(height + 'px');

		if (source_textarea.prop('clientWidth') < source_textarea.prop('scrollWidth')) {
			numLines = source_textarea.val().split('\n').length;
			height += scrollHeight / numLines;
			source_textarea.height(height + 'px');
		}
	}
	source_resize();

	if (subtree.mode == 'raw') {
		return;
	}

	/* Code for edit mode only */
	var title_h1 = $('#content > h1');
	var restore_btn = $('#actionbar a.restore');
	var source_last = source_textarea.val();
	var timeout = null;
	var dmp = new diff_match_patch();

	function source_save_patch(complete) {
		var source_text = source_textarea.val();
		var title_text = title_h1.text();

		if (source_text == source_last && subtree.title == title_text) {
			if (typeof complete == 'function') {
				complete();
			}
			return;
		}

		var patch = dmp.patch_make(source_last, source_text);
		var patch_text = dmp.patch_toText(patch);
		var post_data = {
			action: 'patch',
			patch: patch_text,
		};
		if (subtree.title != title_text) {
			subtree.title = title_text;
			if (subtree.title == '') {
				subtree.title = 'Untitled';
				title_h1.text(subtree.title);
			}
			post_data.title = subtree.title;
			$('title').text(subtree.title + ' - jkent.net');
		}
		$.post(url, post_data, (data) => {
			source_last = source_text;
			subtree.draft = data.draft;
			commit_btn.toggleClass('hidden', !subtree.draft);
			if (typeof complete == 'function') {
				complete();
			}
		});
	}

	source_textarea.on('input', (event) => {
		source_resize();
		if (timeout) {
			clearTimeout(timeout);
			timeout = null;
		}
		timeout = setTimeout(() => {
			source_save_patch();
			timeout = null;
		}, 1000);
	});

	title_h1.prop('contentEditable', true);
	title_h1.addClass('editable');
	title_h1.on('paste', (e) => {
		setTimeout(() => {
			title_h1.html(title_h1.text());
			source_save_patch();
		}, 0);
	}).on('keypress', (e) => {
		if (e.which == 13) {
			title_h1.blur();
			source_save_patch();
			return false;
		}
		if (timeout) {
			clearTimeout(timeout);
			timeout = null;
		}
		timeout = setTimeout(() => {
			source_save_patch();
			timeout = null;
		}, 1000);
		return true;
	});

	restore_btn.on('click', () => {
		if (!confirm('Are you sure you want to restore this version?')) {
			return false;
		}
		if (timeout) {
			clearTimeout(timeout);
			timeout = null;
		}
		$.post(url, {
			action: 'restore',
		}, (data) => {
			var url = new URL(window.location);
			var parsed = parse_pathname(url.pathname);
			url.pathname = build_pathname(parsed.page, null, parsed.path);
			window.location = url;
		});
		return false;
	});
});