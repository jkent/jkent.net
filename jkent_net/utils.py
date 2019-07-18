from flask import request, url_for
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