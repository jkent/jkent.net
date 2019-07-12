from ..auth import admin_required
from ..models import Document, DocumentType, db
from ..models.document import file_extensions
from calendar import monthrange
from datetime import date, timedelta
from flask import Blueprint, Response, current_app, g, redirect, render_template, request, url_for
from flask_menu import register_menu
from html import escape
from jinja2 import Markup
import re

__all__ = ['bp']


date_re = r'^(?P<year>\d{4})(?:-(?P<month>\d{1,2})(?:-(?P<day>\d{1,2}))?)?$'
bp = Blueprint('posts', __name__)


def view_post(post_id):
    document = db.session.query(Document).filter_by(id=post_id).first()
    if not document:
        return 'document not found'

    is_draft = g.user and g.user.is_admin and request.args.get('draft') and document.has_draft
    html = document.draft if is_draft else document.cache

    if request.args.get('raw'):
        raw = document.raw_draft if is_draft else document.raw
        return Response(raw, mimetype='text/plain')

    args ={
        'content': Markup(html),
        'post_id': post_id,
        'doctype': document.type.name,
        'has_draft': g.user and g.user.is_admin and document.has_draft,
        'is_draft': is_draft,
    }
    return render_template('view_post.html', **args)


def edit_post(post_id):
    document = db.session.query(Document).filter_by(id=post_id).first()
    if not document:
        return 'document not found'

    is_draft = g.user and g.user.is_admin and document.has_draft
    raw = document.raw_draft if is_draft else document.raw
    viewonly = not (g.user and g.user.is_admin)

    args = {
        'content': raw,
        'post_id': post_id,
        'viewonly': viewonly,
        'doctype': document.type.name,
        'extension': file_extensions[document.type],
        'has_draft': document.has_draft,
        'has_commit': document.has_commit,
        'is_draft': is_draft,
    }
    return render_template('edit_post.html', **args)


def post_by_id(post_id):
    if request.args.get('source'):
        return edit_post(post_id)
    else:    
        return view_post(post_id)

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

    save = request.form.get('commit')
    if save:
        document.commit()
        return {}

    revert = request.form.get('revert')
    if revert:
        document.revert()
        return {}
        
    patch_text = request.form.get('patch_text')
    if patch_text:
        print(patch_text)
        document.apply_patch(patch_text)
        return {
            'has_draft': document.has_draft,
            'has_commit': document.has_commit,
        }

    doctype = request.form.get('doctype')
    if doctype:
        document.change_type(doctype)
        db.session.add(document)
        db.session.commit()
    
    return {}