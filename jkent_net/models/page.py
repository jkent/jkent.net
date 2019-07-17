from ..models import db
from .subtree import ID_LENGTH

__all__ = ['Page']


class Page(db.Model):
    id = db.Column(db.String(ID_LENGTH), db.ForeignKey('subtree.id'), primary_key=True)
    subtree = db.relationship('Subtree', back_populates='page')
    path = db.Column(db.String(128))
    title = db.Column(db.Unicode(64))
    menu_path = db.Column(db.String(128))
    menu_order = db.Column(db.Integer)

    def __init__(self, subtree, path, menu_path, title, menu_order=0):
        self.subtree = subtree
        self.path = path
        self.menu_path = menu_path
        self.title = title
        self.menu_order = menu_order