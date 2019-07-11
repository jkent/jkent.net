from datetime import datetime
import enum
from flask import current_app, url_for
from html import escape
from jkent_net.models import db
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


markdown_extensions = ['codehilite', 'fenced_code', 'tables']


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
    def source(self):
        filename = self.id + file_extensions[self.type]
        with open(self.source_path, 'r') as f:
            data = f.read()
        return data

    @source.setter
    def source(self, data):
        filename = self.id + file_extensions[self.type]
        with open(self.source_path, 'w') as f:
            f.write(data)

    @property
    def html(self):
        return self.__html__()

    def __html__(self):
        if self.type == DocumentType.html:
            return self.source

        #if self.cache_valid:
        #    with open(self.cache_path, 'r') as f:
        #        return f.read()
        
        with open(self.source_path, 'r') as f:
            input = f.read()

        output = '<div class="rendered">'
        if self.type == DocumentType.markdown:
            output += markdown(input, extensions=markdown_extensions)
        else:
            output += '<pre>' + html.escape(src.read(), False) + '</pre>'
        output += '</div>'

        with open(self.cache_path, 'w') as f:
            f.write(output)

        return output