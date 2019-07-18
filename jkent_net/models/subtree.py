from ..converter import convert_to_html
from ..models import db
from diff_match_patch import diff_match_patch
from flask import current_app
import magic
import os
import random
import re
import string
from sqlalchemy.orm import validates


__all__ = ['Subtree']

ID_LENGTH = 6


class Subtree(db.Model):
    id = db.Column(db.String(ID_LENGTH), primary_key=True)
    owner_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', primaryjoin='Subtree.owner_id==User.id')
    title = db.Column(db.Unicode(256), nullable=True)
    published = db.Column(db.Boolean(), nullable=False, default=False)
    page = db.relationship('Page', uselist=False, back_populates='subtree')

    @staticmethod
    def id_generator():
        while True:
            id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            if not db.session.query(db.exists().where(Subtree.id == id)).scalar():
                break
        return id

    def __init__(self, owner):
        self.id = Subtree.id_generator()
        self.owner = owner

        os.makedirs(os.path.join(current_app.repository.path, self.id), exist_ok=True)

    @validates('id')
    def validate_id(self, key, id):
        assert re.match(r'[A-Za-z0-9]{{{}}}'.format(ID_LENGTH), id)
        return id

    def exists(self, path, version='HEAD'):
        if version:
            return current_app.repository.exists(os.path.join(self.id, path), version)

        return os.path.exists(os.path.join(current_app.repository.path, self.id, path))

    def find_index(self, path, version='HEAD'):
        if self.exists(os.path.join(path, 'index.html'), version):
            return os.path.join(path, 'index.html')
        elif self.exists(os.path.join(path, 'index.htm'), version):
            return os.path.join(path, 'index.htm')
        elif self.exists(os.path.join(path, 'index.md'), version):
            return os.path.join(path, 'index.md')
        elif self.exists(os.path.join(path, 'index.txt'), version):
            return os.path.join(path, 'index.txt')
        else:
            return None

    def _mimetype_from_path(self, path):
        if path.endswith(('.html', '.htm')):
            return 'text/html'
        elif path.endswith('.md'):
            return 'text/markdown'
        elif path.endswith('.txt'):
            return 'text/plain'
        return None

    def open(self, path, version='HEAD', raw=False):
        fragment = False
        mimetype = self._mimetype_from_path(path)
        if not raw and version:
            rows = current_app.repository.history(os.path.join(self.id, path), version, 1)
            if not rows:
                return None, mimetype, fragment
            hash = rows[0][0]

            # check for cache hit
            cache_path = os.path.join(current_app.cache_root, self.id, hash, path)
            if os.path.exists(cache_path):
                file = open(cache_path, 'rb')
                if mimetype == 'text/html':
                    buf = file.read(16384)
                    fragment = b'<title>' not in buf
                    file.seek(0)
                elif mimetype.startswith('text/'):
                    fragment = True
                    mimetype = 'text/html'
                elif mimetype == None:
                    mimetype = magic.from_buffer(file.read(1024), mime=True)
                    file.seek(0)
                return file, mimetype, fragment

        # raw or cache miss or non-cacheable
        file = current_app.repository.read(os.path.join(self.id, path), version)
        if file == None:
            return None, mimetype, fragment
        if mimetype == None:
            mimetype = magic.from_buffer(file.read(1024), mime=True)
            file.seek(0)

        if raw and mimetype == 'text/html':
            buf = file.read(16384)
            fragment = b'<title>' not in buf
            file.seek(0)
        elif raw and mimetype.startswith('text/'):
            fragment = True
        elif mimetype.startswith('text/'):
            file, fragment = convert_to_html(file, mimetype)
            mimetype = 'text/html'

        if not raw and version:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            cache = open(cache_path, 'wb')
            while True:
                buf = file.read(16384)
                if not buf:
                    break
                cache.write(buf)
            cache.close()
            file.seek(0)

        return file, mimetype, fragment

    def write(self, path, data):
        current_app.repository.write(os.path.join(self.id, path), data)

    def commit(self, message=''):
        current_app.repository.add(self.id)
        current_app.repository.commit(message)

    def revert(self, version='HEAD'):
        current_app.repository.checkout(self.id, version)

    def patch(self, path, patch_text):
        file, mimetype = self.open(path, None)
        data = file.read()
        dmp = diff_match_patch()
        patch = dmp.patch_fromText(patch_text)
        data, hunks_ok = dmp.patch_apply(patch, data)
        self.write(path, data)
        return all(hunks_ok)
    
    def list(self, path, version=None):
        return current_app.repository.list(os.path.join(self.id, path), version)

    def isdir(self, path, version=None):
        return current_app.repository.isdir(os.path.join(self.id, path), version)

    def history(self, path, version=None, num=None):
        return current_app.repository.history(os.path.join(self.id, path), version, num)

    def diff(self, path='', version1=None, version2=None):
        if path == None:
            path = ''
        return current_app.repository.diff(os.path.join(self.id, path), version1, version2)