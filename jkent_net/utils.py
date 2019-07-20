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
        current_menu.pop(menu)
    else:
        current_menu._child_entries = \
            {k:v for k, v in current_menu._child_entries.items() if v != menu}

def update_menus():
    for page in Page.query:
        current_menu.submenu(page.menu_path).register(
            'pages.pages', page.title, order=page.menu_order,
            endpoint_arguments_constructor=partial(lambda p: {'name': p}, page.name))