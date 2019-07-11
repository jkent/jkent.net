from ..models import db
from datetime import datetime
import enum
from flask import current_app, url_for
from html import escape
from markdown import markdown
import random
import string
import os


__all__ = ['Document', 'DocumentType']


def generate_id():
    while True:
        id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        if not db.session.query(db.exists().where(Document.id == id)).scalar():
            break
    return id


class DocumentType(enum.Enum):
    text = 0
    html = 1
    markdown = 2


file_extensions = {
    DocumentType.text: '.txt',
    DocumentType.html: '.html',
    DocumentType.markdown: '.md',
}


markdown_extensions = [
    'jkent_net.markdown.codehilite:CodeHiliteExtension',
    'jkent_net.markdown.fenced_code:FencedCodeExtension',
    'tables'
]


class Document(db.Model):   
    id = db.Column(db.String(6), primary_key=True, default=generate_id)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    type = db.Column(db.Enum(DocumentType), nullable=False, default=DocumentType.text)
    title = db.Column(db.Unicode(128), nullable=False)
    page_name = db.Column(db.Unicode(64)) # if null, post
    published_time = db.Column(db.DateTime) # if null, not publshed

    def __repr__(self):
        return '<Document %r>' % self.id

    @property
    def source_relative_path(self):
        filename = self.id + file_extensions[self.type]
        return os.path.join('documents', filename)

    @property
    def source_path(self):
        return os.path.join(current_app.repo_path, self.source_relative_path)

    @property
    def cache_path(self):
        filename = self.id + '.html'
        return os.path.join(current_app.cache_path, 'documents', filename)

    @property
    def cache_valid(self):
        source_timestamp = current_app.repo.get_timestamp(self.source_relative_path)
        if not source_timestamp:
            source_timestamp = os.path.getmtime(self.source_relative_path)

        if self.type == DocumentType.html:
            return False

        try:
            cache_timestamp = os.path.getmtime(self.cache_path)
        except FileNotFoundError:
            return False

        return source_timestamp <= cache_timestamp

    @property
    def source_draft(self):
        try:
            with open(self.source_path, 'r') as f:
                data = f.read()
        except:
            data = ''
        return data

    @source_draft.setter
    def source_draft(self, data):
        with open(self.source_path, 'w') as f:
            f.write(data)

    @property
    def source(self):
        return current_app.repo.get_index(self.source_relative_path) or ''

    @property
    def html(self):
        #if self.cache_valid:
        #    with open(self.cache_path, 'r') as f:
        #        return f.read()

        output = '<div class="rendered">'
        if self.type == DocumentType.markdown:
            output += markdown(self.source, extensions=markdown_extensions)
        elif self.type == DocumentType.html:
            output += self.source
        else:
            output += '<pre>' + escape(self.source, False) + '</pre>'
        output += '</div>'

        with open(self.cache_path, 'w') as f:
            f.write(output)
        
        return output

    @property
    def html_draft(self):
        with open(self.source_path, 'r') as f:
            input = f.read()

        output = '<div class="rendered">'
        if self.type == DocumentType.markdown:
            output += markdown(input, extensions=markdown_extensions)
        elif self.type == DocumentType.html:
            output += input        
        else:
            output += '<pre>' + escape(input, False) + '</pre>'
        output += '</div>'

        return output

    def get_info(self):
        return current_app.repo.get_info(self.source_relative_path)

    @property
    def has_draft(self):
        return self.get_info()['modified']

    def revert(self):
        current_app.repo.checkout(self.source_relative_path)
    
    def save(self):
        current_app.repo.add(self.source_relative_path)
        current_app.repo.commit()

    def change_type(self, type):
        src = self.source_path
        self.type = DocumentType[type]
        dst = self.source_path
        current_app.repo.move(src, dst)
    