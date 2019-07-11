from calendar import monthrange
from datetime import date, timedelta
from flask import Blueprint, Response, g, render_template, request, url_for
from flask_menu import register_menu
from html import escape
from jinja2 import Markup
from jkent_net.auth import admin_required
from jkent_net.models import Document, DocumentType, db
import re

__all__ = ['bp']


date_re = r'^(?P<year>\d{4})(?:-(?P<month>\d{1,2})(?:-(?P<day>\d{1,2}))?)?$'
bp = Blueprint('posts', __name__)


def post_by_id(post_id):
    document = db.session.query(Document).filter_by(id=post_id).first()
    if not document:
        return 'document not found'

    raw = request.args.get('raw')
    source = request.args.get('source')
    if raw:
        return Response(document.source, mimetype='text/plain')
    elif source:
        html = '<pre>' + escape(document.source) + '</pre>'
    else:
        html = document.html

    args = {
        'content': Markup(html),
        'post_id': post_id,
        'source': source,
        'markdown': document.type == DocumentType.markdown
    }

    return render_template('post.html', **args)

def posts_by_date(start_date=None, end_date=None):
    return 'posts from %s to %s' % (start_date, end_date)

@bp.route('/')
@register_menu(bp, '.', 'Home')
def index():
    return render_template('index.html')
    return posts_by_date()

@bp.route('/p/<path:path>')
def p(path):
    parts = path.split('/')
    m = re.match(date_re, parts[0])
    if not m:
        return post_by_id(parts[0])

    start_year = int(m.group('year'))
    start_month = int(m.group('month') or 1)
    start_day = int(m.group('day') or 1)
    start_date = date(start_year, start_month, start_day)

    if len(parts) == 3:
        m = re.match(date_re, parts[2])
        if not m or parts[1] not in ('to', 'thru'):
            raise Exception('unknown url scheme')

        if parts[1] == 'to':
            end_year = int(m.group('year'))
            end_month = int(m.group('month') or 1)
            end_day = int(m.group('day') or 1)
            end_date = date(end_year, end_month, end_day) - timedelta(days=1)
            assert(start_date <= end_date)
            return posts_by_date(start_date, end_date)

    end_year = int(m.group('year'))
    end_month = int(m.group('month') or 12)
    end_day = int(m.group('day') or monthrange(end_year, end_month)[1])
    end_date = date(end_year, end_month, end_day)
    assert(start_date <= end_date)
    return posts_by_date(start_date, end_date)

@bp.route('/p/<string:post_id>', methods=['POST'])
@admin_required
def p_edit(post_id):
    document = db.session.query(Document).filter_by(id=post_id).first()
    if not document:
        return 'document not found'

    document.source = request.form['markdown']

    return post_by_id(post_id)