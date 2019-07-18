$(function(){
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
  var url = new URL(window.location);
  url.search = '';

  var source = $('#content > textarea.source');
  var source_last = source.val();
  var source_timeout = null;
  var dmp = new diff_match_patch();
  var commit_btn = $('#actionbar a.commit');
  var restore_btn = $('#actionbar a.restore');
  var draft_btn = $('#actionbar a.draft');
  var raw_btn = $('#actionbar a.raw');
  var edit_btn = $('#actionbar a.edit');
  var title_btn = $('#actionbar a.title');

  function parse_pathname(pathname) {
      match = pathname.match(/^\/(?<page>\w+)(?:\/_(?<version>\w+))?(?:\/(?<path>\w+))?/);
      console.log(match.groups);
      return match.groups;
  }

  function build_pathname(page_part, version, path) {
      var pathname = page_part;
      if (version) {
          pathname += '/_' + version;
      }
      if (path) {
          pathname += '/' + path;
      }
      return pathname;
  }

  function source_save_patch(complete) {
      if (page.mode == 'render' || page.mode == 'raw') {
          commit_btn.toggleClass('hidden', !page.draft);
          if (typeof complete == 'function') {
              complete();
          }
          return;
      }

      var source_text = source.val();
      var patch = dmp.patch_make(source_last, source_text);
      var patch_text = dmp.patch_toText(patch);
      $.post(url, {
          action: 'patch',
          patch: patch_text,
      }, (data) => {
          source_last = source_text;
          page.draft = data.draft;
          commit_btn.toggleClass('hidden', !page.draft);
          if (typeof complete == 'function') {
              complete();
          }
      });
  }

  function source_resize() {
      source.height('inherit');
      var scrollHeight = source.prop('scrollHeight');
      var height = parseInt(source.css('border-top-width'), 10)
                 - parseInt(source.css('padding-top'), 10)
                 + scrollHeight
                 - parseInt(source.css('padding-bottom'), 10)
                 + parseInt(source.css('border-bottom-width'), 10);

      source.height(height + 'px');

      if (source.prop('clientWidth') < source.prop('scrollWidth')) {
          numLines = source.val().split('\n').length;
          height += scrollHeight / numLines;
          source.height(height + 'px');
      }
  }
  source_resize();

  source.on('input', (event) => {
      source_resize();
      if (source_timeout) {
          clearTimeout(source_timeout);
          source_timeout = null;
      }
      source_timeout = setTimeout(() => {
          source_save_patch();
          source_timeout = null;
      }, 1000);
  });
  
  commit_btn.on('click', () => {
      if (source_timeout) {
          clearTimeout(source_timeout);
          source_timeout = null;
      }
      source_save_patch(() => {
          $.post(url, {
              action: 'commit',
          }, (data) => {
              window.location = url;
          });
      });
      return false;
  });

  restore_btn.on('click', () => {
      if (!confirm('Are you sure you want to restore this version?')) {
          return false;
      }
      if (source_timeout) {
          clearTimeout(source_timeout);
          source_timeout = null;
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

  raw_btn.on('click', () => {
      var search = new URLSearchParams();
      if (page.mode != 'raw' || page.mode == 'edit') {
          search.set('raw', '1');
      }
      url.search = search;
      window.location = url;
      return false;
  });

  edit_btn.on('click', () => {
      var search = new URLSearchParams();
      if (page.mode != 'edit' || page.mode == 'raw') {
          search.set('edit', '1');
      }
      url.search = search;
      window.location = url;
      return false;
  });

  title_btn.on('click', () => {
      var input_span = $('#actionbar span.input');
      var title_input = $('#actionbar input.title');
      if (!title_input.length) {
          input_span.html('<label>Title <input type="text" class="title" placeholder="Title"></label>');
          title_input = $('#actionbar input.title');
          title_input.val(title);
          title_btn.toggleClass('highlight', true);
          title_input.on('keydown', (event) => {
              if (event.key === 'Enter') {
                  page.title = title_input.val();
                  $.post(url, {
                      action: 'set-title',
                      title: page.title,
                  }, () => {
                      $('title').text(page.title + ' - jkent.net');
                      input_span.html('');
                      title_btn.toggleClass('highlight', false);
                  });
              }
          });
      } else {
          input_span.html('')
          title_btn.toggleClass('highlight', false);
      }
  });

  draft_btn.on('click', () => {
      var parts = window.location.pathname.slice(1).split('/');        
      var page_part = parts.shift();
      var pathname;
      if (page.version == null) {
          pathname = '/' + page_part + '/_HEAD';
      } else {
          var _ = parts.shift();
          pathname = '/' + page_part
      }
      if (parts.length > 0 && parts[0] != '') {
          pathname += '/' + parts.join('/');
      }
      window.location.pathname = pathname;
      return false;
  });

  source.prop('readonly', page.mode != 'edit');
});