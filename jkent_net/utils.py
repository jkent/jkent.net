from .models import Page
from flask import request, url_for
from flask_menu import current_menu
from flask_security.core import current_user
from functools import partial
from werkzeug.urls import url_join, url_parse

def is_safe_url(target):
    ref_url = url_parse(request.host_url)
    test_url = url_parse(url_join(request.host_url, target))
    if test_url.path == '/login':
        return False
    return test_url.scheme == ref_url.scheme or ref_url.scheme == 'https' and \
        test_url.netloc == ref_url.netloc 

def get_redirect_target(endpoint, **values):
    for target in request.values.get('r'), request.referrer, url_for(endpoint, **values):
        if not target:
            continue
        if is_safe_url(target):
            return target

def remove_menu(menu):
    if type(menu) is str:
        menu = current_menu.submenu(menu)
    current_menu._child_entries = \
        {k:v for k, v in current_menu._child_entries.items() if v != menu}

def update_menus():
    for page in Page.query:
        current_menu.submenu(page.menu_path).register(
            'pages.pages', page.title, order=page.menu_order,
            endpoint_arguments_constructor=partial(lambda p: {'name': p}, page.name))

class Pager(object):
    def __init__(self, items_per_page):
        self._items_per_page = items_per_page
        self._item_count = 0
        self._page = 1

    @property
    def items(self):
        return self._item_count

    @items.setter
    def items(self, item_count):
        self._item_count = item_count

    @property
    def items_per_page(self):
        return self._items_per_page

    @property
    def count(self):
        return (self._item_count + self._items_per_page - 1) // self._items_per_page

    @property
    def first(self):
        return 1

    @property
    def last(self):
        return self.count

    @property
    def next(self):
        return min(self._page + 1, self.count)

    @property
    def prev(self):
        return max(self._page - 1, 1)

    @property
    def offset(self):
        return (self._page - 1) * self._items_per_page

    @property
    def page(self):
        return self._page
    
    @page.setter
    def page(self, value):
        self._page = value

    def range(self, num_links):
        lb = max(min(self.count, self.page + num_links//2) - num_links, 0) + 1
        ub = min(max(0, self.page - num_links//2) + num_links, self.count) + 1
        return range(lb, ub)