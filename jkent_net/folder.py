from flask_security import AnonymousUser, current_user
import os
import random
import re
import string
import yaml


class Folder:
    @classmethod
    def create(cls, repo):
        while True:
            folder_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            if not repo.exists(os.path.join('folders', folder_id, '.metadata.yml')):
                break

        os.makedirs(os.path.join(repo.path, 'folders', folder_id), exist_ok=True)
        metadata = {'viewers': [], 'editors': []}
        with open(os.path.join(repo.path, 'folders', folder_id, '.metadata.yml'), 'w') as f:
            yaml.dump(metadata, f)

        return cls(repo, folder_id)

    def __init__(self, repo, folder_id, version=None):
        self._repo = repo
        self._folder_id = folder_id
        self._version = version
        with open(os.path.join(repo.path, 'folders', folder_id, '.metadata.yml'), 'r') as f:
            self._metadata = yaml.load(f, Loader=yaml.SafeLoader)

    def _save_metadata(self):
        if self._version != None:
            raise Exception
        with open(os.path.join(repo.path, 'folders', folder_id, '.metadata.yml'), 'w') as f:
            yaml.dump(self._metadata, f)

    @property
    def repo(self):
        return self._repo

    @property
    def id(self):
        return self._folder_id

    @property
    def version(self):
        return self._version
    
    @version.setter
    def version(self, value):
        self._version = value

    @property
    def path(self):
        return os.path.join('folders', self.id)

    @property
    def viewers(self):
        return self._metadata.get('viewers', []).copy()
    
    @viewers.setter
    def viewers(self, value):
        if self._version != None:
            raise Exception
        self._metadata['viewers'] = list(value)
        self._save_metadata()

    @property
    def editors(self):
        return self._metadata.get('editors', []).copy()

    @editors.setter
    def editors(self, value):
        if self._version != None:
            raise Exception
        self._metadata['editors'] = list(value)
        self._save_metadata()

    def can_read(self):
        if current_user.any_role('admin'):
            return True
        if current_user.any_role(*self.editors):
            return True
        if current_user.any_role(*self.viewers):
            return True
        return False

    def can_write(self):
        if current_user.any_role('admin'):
            return True
        if current_user.any_role(*self.editors):
            return True
        return False

    def exists(self, path):
        if re.match('^\.|/\.', path):
            return False
        path = os.path.join(self.path, path)
        return self._repo.exists(path, self._version)

    def isdir(self, path):
        if re.match('^\.|/\.', path):
            return False
        path = os.path.join(self.path, path)
        return self._repo.isdir(path, self._version)

    def open(self, path, mode):
        if 'w' in mode:
            if self._version != None:
                raise Exception
            if not self.can_write():
                raise PermissionError
        elif 'r' in mode:
            if not self.can_read():
                raise PermissionError

        if re.match('$\.|/\.', path):
            raise FileNotFoundError

        path = os.path.join(self.path, path)
        return self._repo.open(path, mode, self._version)

    def find_index(self, path='.'):
        if not self.can_read():
            raise PermissionError

        for filename in ('index.html', 'index.htm', 'index.md', 'index.txt'):
            probe_path = os.path.join(path, filename)
            if self.exists(probe_path):
                return probe_path
        raise FileNotFoundError

    def list(self, path='.', recursive=False):
        if not self.can_read():
            raise PermissionError

        path = os.path.normpath(os.path.join(self.path, path))
        paths = self._repo.list(path, self._version, recursive)
        paths = filter(lambda x: not re.match('^\.|/\.', x), paths)
        return list(paths)