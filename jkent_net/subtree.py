from .converter import convert_to_html
from diff_match_patch import diff_match_patch
from io import BytesIO
import magic
import os
import re
import string

ID_LENGTH = 6


class Subtree(object):
    def __init__(self, repository, cache_root, id=None):
        self._repository = repository
        if id:
            if not re.match(r'[A-Za-z0-9]{{{}}}'.format(ID_LENGTH), id):
                raise ValueError('id is invalid')
            self._exists = os.path.exists(os.path.join(repository.path, id))
        else:
            while True:
                id = ''.join(random.choices(string.ascii_letters + string.digits, k=ID_LENGTH))
                if not os.path.exists(os.path.join(repository.path, id)):
                    break
            self._exists = False
        self._cache_root = cache_root
        self._id = id

    @property
    def id(self):
        return self._id

    @property
    def exists(self):
        return self._exists

    def create(self):
        if self._exists:
            raise Exception('subtree exists')
        
        os.mkdir(os.path.join(self._repository.path, self._id))
        self._exists = True

    def file_exists(self, path, version='HEAD'):
        if version:
            return self._repository.exists(os.path.join(self._id, path), version)

        return os.path.exists(os.path.join(self._repository.path, self._id, path))

    def _find_index(self, path, version=None):
        if self.file_exists(os.path.join(path, 'index.html'), version):
            return os.path.join(path, 'index.html')
        elif self.file_exists(os.path.join(path, 'index.htm'), version):
            return os.path.join(path, 'index.htm')
        elif self.file_exists(os.path.join(path, 'index.md'), version):
            return os.path.join(path, 'index.md')
        elif self.file_exists(os.path.join(path, 'index.txt'), version):
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

    def read_raw(self, path, version='HEAD'):
        if path.endswith('/'):
            path = self._find_index(path, version)
            if not path:
                return None, None
        mimetype = self._mimetype_from_path(path)
        file = self._repository.read(os.path.join(self._id, path), version)
        if file == None:
            return None, None
        if mimetype == None:
            mimetype = magic.from_buffer(file.read(1024), mime=True)
            file.seek(0)
        return file, mimetype

    def read(self, path, version='HEAD'):
        if path.endswith('/'):
            path = self._find_index(path, version)
            if not path:
                return None, None
        mimetype = self._mimetype_from_path(path)

        if version != None:
            hash = self._repository.log(os.path.join(self._id, path), version, 1)
            if not hash:
                return None, None

            # check for cache hit
            cache_path = os.path.join(self._cache_root, self._id, hash, path)
            if os.path.exists(cache_path):
                file = open(cache_path, 'rb')
                if mimetype in ['text/markdown', 'text/plain']:
                    mimetype = 'text/html'
                elif mimetype == None:
                    mimetype = magic.from_buffer(file.read(1024), mime=True)
                    file.seek(0)
                return file, mimetype

        # cache miss or non-cacheable
        file, mimetype = self.read_raw(path, version)
        if mimetype == 'text/html' and data.find('<title>') >= 0:
            pass
        elif mimetype in ('text/html', 'text/markdown', 'text/plain'):
            file = convert_to_html(file, mimetype)
            mimetype = 'text/html'

        if version != None:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            cache = open(cache_path, 'wb')
            while True:
                buf = file.read(16384)
                if not buf:
                    break
                cache.write(buf)
            cache.close()
            file.seek(0)

        return file, mimetype

    def write(self, path, data):
        self._repository.write(os.path.join(self._id, path), data)

    def commit(self, path, message=None):
        self._repository.add(path)
        self._repository.commit(message)

    def revert(self, version='HEAD'):
        self._repository.checkout(self, self._id, version)

    def patch(self, path, patch_text):
        data = self.read(self, path)
        dmp = diff_match_patch()
        patch = dmp.patch_fromText(patch_text)
        data, hunks_ok = dmp.patch_apply(patch, text)
        self.write(path, data)
        return all(hunks_ok)
    
    def list(self, path, version=None):
        return self._repository.list(os.path.join(self._id, path), version)