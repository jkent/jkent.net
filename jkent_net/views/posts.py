from ..auth import admin_required
from ..models import Document, DocumentType, db
from ..models.document import file_extensions
from calendar import monthrange
from datetime import date, timedelta
import patch
from flask import Blueprint, Response, current_app, g, redirect, render_template, request, url_for
from flask_menu import register_menu
from html import escape
from jinja2 import Markup
import re

__all__ = ['bp']


date_re = r'^(?P<year>\d{4})(?:-(?P<month>\d{1,2})(?:-(?P<day>\d{1,2}))?)?$'
bp = Blueprint('posts', __name__)


def post_by_id(post_id):
    document = db.session.query(Document).filter_by(id=post_id).first()
    if not document:
        return 'document not found'

    if g.user and g.user.is_admin:
        revert = request.args.get('revert')
        if revert:
            document.revert()
            return redirect(url_for('posts.p', path=post_id, source=1))
        
        save = request.args.get('save')
        if save:
            document.save()
            return redirect(url_for('posts.p', path=post_id))

    if request.args.get('raw'):
        if g.user and g.user.is_admin and request.args.get('draft'): 
            source = document.source_draft
        else:
            source = document.source
        return Response(source, mimetype='text/plain')

    if request.args.get('source'):
        if g.user and g.user.is_admin and document.has_draft:
            source = document.source_draft
            is_draft = True
        else:
            source = document.source
            is_draft = False

        args = {
            'content': source[:-1],
            'post_id': post_id,
            'viewonly': not g.user or not g.user.is_admin,
            'doctype': document.type.name,
            'is_draft': is_draft,
            'extension': file_extensions[document.type],
        }
        args.update(document.get_info())
        return render_template('edit_post.html', **args)

    if g.user and g.user.is_admin and request.args.get('draft') and document.has_draft:
        html = document.html_draft
        is_draft = True
    else:
        html = document.html
        is_draft = False

    args ={
        'content': Markup(html),
        'post_id': post_id,
        'doctype': document.type.name,
        'is_draft': is_draft,
    }
    return render_template('view_post.html', **args)

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

    diff = request.form.get('diff')
    if diff:
        ps = patch.fromstring(diff.encode('utf-8'))
        ps.apply(1, current_app.repo_path)
        return document.get_info()

    doctype = request.form.get('doctype')
    if doctype:
        document.change_type(doctype)
        db.session.add(document)
        db.session.commit()
    
    return {}