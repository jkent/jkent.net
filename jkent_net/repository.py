from io import BytesIO
import os
import subprocess


class Repository:
    def __init__(self, path):
        self._path = path
        if not os.path.exists(os.path.join(self._path, '.git')):
            os.makedirs(self._path, exist_ok=True)
            subprocess.check_call(['/usr/bin/git', '-C', self._path, 'init'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @property
    def path(self):
        return self._path

    def exists(self, path, version=None):
        if version == None:
            return os.path.exists(os.path.join(self.path, path))
        else:
            try:
                subprocess.check_call(['/usr/bin/git', '-C', self._path, 'cat-file',
                    '-e', '{}:{}'.format(version, path)], stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                return False
            return True

    def open(self, path, mode, version=None):
        if not version:
            return open(os.path.join(self._path, path), mode)
        elif version and 'r' in mode:
            try:
                data = subprocess.check_output(['/usr/bin/git', '-C',
                    self._path, 'cat-file', '-p',
                    '{}:{}'.format(version, path)], stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                raise FileNotFoundError
            return BytesIO(data)
        elif version and 'w' in mode:
            raise ValueError

    def checkout(self, path, version):
        if version == None:
            raise ValueError

        subprocess.check_call(['/usr/bin/git', '-C', self._path, 'checkout',
            version, '--', path])
        subprocess.check_call(['/usr/bin/git', '-C', self._path, 'clean', '-fd',
            '--', path])

    def add(self, path='.'):
        subprocess.check_call(['/usr/bin/git', '-C', self._path, 'add', path])
    
    def commit(self, message=''):
        command = ['/usr/bin/git', '-C', self._path, 'commit', '-q',
            '--allow-empty-message', '-m', message]
        subprocess.check_call(command)

    def history(self, path=None, version=None, num=None):
        if not version:
            raise ValueError

        try:
            result = subprocess.check_output(['/usr/bin/git', '-C', self._path,
                'log'] + (['-n{}'.format(num)] if num else []) +
                ['--pretty=format:%H %at %ae %s', version, '--', path],
                stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            return ''

        results = []
        for line in result.rstrip().decode('utf8').split('\n'):
            if line:
                line = tuple(line.split(' ', 3))
                if self.exists(path, line[0]):
                    results.append(line)
        return results

    def list(self, path, version=None, recursive=False):
        path = os.path.normpath(path)
        if not self.isdir(path, version):
            return ValueError
        if not path.endswith('/'):
            path += '/'
        if version:
            try:
                result = subprocess.check_output(['/usr/bin/git', '-C',
                    self._path, 'ls-tree'] + (['-r'] if recursive else []) +
                    [version, '--', path],
                    stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                return []

            paths = []
            lines = result.decode('utf8').rstrip().split('\n')
            for line in lines:
                _, type_, _, filename = line.split(None, 3)
                if type_ == 'tree':
                    filename += '/'
                paths.append(filename)

            paths = list(map(lambda x: x[len(path):], paths))
        else:
            path = os.path.dirname(os.path.join(self._path, path))
            paths = []
            for root, dirs, files in os.walk(os.path.join(self._path, path)):
                for dir in dirs:
                    dirname = os.path.normpath(os.path.join(root, dir)) + os.sep
                    paths.append(dirname)
                if recursive:
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                else:
                    dirs[:] = []
                for file in files:
                    filename = os.path.normpath(os.path.join(root, file))
                    paths.append(filename)

            paths = list(map(lambda x: x[len(path) + 1:], paths))

        paths.sort()
        return paths

    def isdir(self, path, version=None):
        if version:
            try:
                result = subprocess.check_output(['/usr/bin/git', '-C',
                    self._path, 'ls-tree', '-r', '--name-only', version, '--',
                    path], stderr=subprocess.DEVNULL)
                return result.rstrip().split(b'\n')[0].decode('utf8') != path
            except subprocess.CalledProcessError:
                return False
            except:
                return False
        else:
            return os.path.isdir(os.path.join(self._path, path))

    def diff(self, path, version1=None, version2=None):
        if version1 == version2:
            return False
        try:
            if version1 == None:
                subprocess.check_call(['/usr/bin/git', '-C', self._path, 'diff',
                    '--exit-code', '--quiet', version2, '--', path])
            elif version2 == None:
                subprocess.check_call(['/usr/bin/git', '-C', self._path, 'diff',
                    '--exit-code', '--quiet', '-R', version1, '--', path])
            else:
                subprocess.check_call(['/usr/bin/git', '-C', self._path, 'diff',
                    '--exit-code', '--quiet', version1, version2, '--', path])
        except subprocess.CalledProcessError:
            return True
        return False