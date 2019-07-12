from ..models import db
from datetime import datetime
from diff_match_patch import diff_match_patch
import enum
from flask import current_app, url_for
from html import escape
from markdown import markdown
import os
import random
import shutil
import string
import subprocess


__all__ = ['Document', 'DocumentType']


def id_generator():
    while True:
        id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        if not db.session.query(db.exists().where(Document.id == id)).scalar():
            break
    return id

def text_converter(data):
    output = '<div class="rendered"><pre>'
    output += escape(data)
    output += '</pre></div>'
    return output

def html_converter(data):
    output = '<div class="rendered">'
    output += data
    output += '</div>'
    return output

def markdown_converter(data):
    output = '<div class="rendered">'
    output += markdown(data, extensions=[
        'jkent_net.markdown.codehilite:CodeHiliteExtension',
        'jkent_net.markdown.fenced_code:FencedCodeExtension',
        'tables',
    ])
    output += '</div>'
    return output


class DocumentType(enum.Enum):
    text = 0
    html = 1
    markdown = 2

file_extensions = {
    DocumentType.text: '.txt',
    DocumentType.html: '.html',
    DocumentType.markdown: '.md',
}

converters = {
    DocumentType.text: text_converter,
    DocumentType.html: html_converter,
    DocumentType.markdown: markdown_converter,
}


class Document(db.Model):   
    id = db.Column(db.String(6), primary_key=True, default=id_generator)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    type = db.Column(db.Enum(DocumentType), nullable=False, default=DocumentType.text)
    title = db.Column(db.Unicode(128), nullable=False)
    page_name = db.Column(db.Unicode(64)) # if null, post
    published_time = db.Column(db.DateTime) # if null, not publshed

    def __repr__(self):
        return '<Document %r>' % self.id

    @property
    def relative_path(self):
        return self.id

    @property
    def path(self):
        path = os.path.join(current_app.repository_path, self.relative_path)
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def cache_path(self):
        path = os.path.join(current_app.cache_path, self.relative_path)
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def index_relative_path(self):
        path = os.path.join(self.relative_path, 'index{}'.format(file_extensions[self.type]))
        return path

    @property
    def index_path(self):
        path = os.path.join(current_app.repository_path, self.index_relative_path)
        return path        

    @property
    def cache(self):
        if not current_app.repository.file_exists(self.index_relative_path):
            return ''

        src_timestamp = current_app.repository.timestamp(self.relative_path)

        try:
            dst = os.path.join(self.cache_path, 'index.html')
            dst_timestamp = os.path.getmtime(dst)
        except FileNotFoundError:
            dst_timestamp = 0

        if src_timestamp < dst_timestamp:
            with open(dst, 'r') as f:
                return f.read()

        converter = converters[self.type]
        data = current_app.repository.cat(self.index_relative_path)
        data = converter(data)
        with open(dst, 'w') as f:
            f.write(data)

        return data

    @property
    def raw(self):
        return current_app.repository.cat(self.index_relative_path)

    @property
    def draft(self):
        try:
            src = os.path.join(self.index_path)
            with open(src, 'r') as f:
                data = f.read()
        except:
            data = ''
        
        converter = converters[self.type]
        data = converter(data)
        return data

    @draft.setter
    def draft(self, data):
        with open(self.index_path, 'w') as f:
            f.write(data)

    @property
    def raw_draft(self):
        try:
            with open(self.index_path, 'r') as f:
                data = f.read()
        except:
            data = ''
        return data

    @property
    def has_draft(self):
        return current_app.repository.is_dirty(self.index_relative_path)

    @property
    def has_commit(self):
        return not current_app.repository.is_unknown(self.index_relative_path)

    def apply_patch(self, patch_text):
        print(self.path)
        print(self.index_path)
        try:
            with open(self.index_path, 'r') as f:
                text = f.read()
        except FileNotFoundError:
            text = ''

        dmp = diff_match_patch()
        patch = dmp.patch_fromText(patch_text)
        text, _ = dmp.patch_apply(patch, text)
        
        with open(self.index_path, 'w') as f:
            f.write(text)

    def revert(self):
        if current_app.repository.is_unknown(self.relative_path):
            shutil.rmtree(self.path)
        else:
            current_app.repository.checkout(self.relative_path)

    def commit(self):
        current_app.repository.add(self.relative_path)
        current_app.repository.commit()

    def change_type(self, new_type):
        if self.type == new_type:
            return
        src = os.path.join(self.path, 'index{}'.format(file_extensions[self.type]))
        self.type = new_type
        dst = os.path.join(self.path, 'index{}'.format(file_extensions[self.type]))
        os.rename(src, dst)
        db.session.add(self)
        db.session.commit()