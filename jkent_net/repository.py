from io import BytesIO
import os
import subprocess


class Repository:
    def __init__(self, path):
        self._path = path
        if not os.path.exists(os.path.join(self._path, '.git')):
            os.makedirs(self._path, exist_ok=True)
            subprocess.check_call(['git', '-C', self._path, 'init'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @property
    def path(self):
        return self._path

    def exists(self, path, version='HEAD'):
        try:
            subprocess.check_call(['git', '-C', self._path, 'cat-file', '-e',
                '{}:{}'.format(version, path)], stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            return False
        return True

    def read(self, path, version='HEAD'):
        if not version:
            if not os.path.isfile(os.path.join(self._path, path)):
                return None
            try:
                file = open(os.path.join(self._path, path), 'rb')
            except FileNotFoundError:
                return None
            return file
        else:
            try:
                data = subprocess.check_output(['git', '-C', self._path,
                    'cat-file', '-p', '{}:{}'.format(version, path)],
                    stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                return None
            return BytesIO(data)

    def write(self, path, data):
        with open(os.path.join(self._path, path), 'wb') as f:
            f.write(data)

    def checkout(self, path, version='HEAD'):
        subprocess.check_call(['git', '-C', self._path, 'checkout', version,
            '--', path])
        subprocess.check_call(['git', '-C', self._path, 'clean', '-fd', '--',
            path])

    def add(self, path):
        subprocess.check_call(['git', '-C', self._path, 'add', path])
    
    def commit(self, message=None):
        command = ['git', '-C', self._path, 'commit', '-q',
            '--allow-empty-message']
        if message:
            command += ['-m', message]
        subprocess.check_call(command)

    def history(self, path=None, version='HEAD', num=None):
        if not version:
            return []

        try:
            result = subprocess.check_output(['git', '-C', self.path, 'log'] +
                (['-n{}'.format(num)] if num else []) +
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

    def list(self, path, version='HEAD', recursive=False):
        if version:
            try:
                prefix = os.path.dirname(path)
                result = subprocess.check_output(['git', '-C', self.path,
                    'ls-tree'] + (['-r'] if recursive else []) + ['--name-only',
                    version, '--', path], stderr=subprocess.DEVNULL)
                paths = result.rstrip().split(b'\n')
            except subprocess.CalledProcessError:
                paths = []
        else:
            prefix = os.path.dirname(os.path.join(self._path, path))
            paths = []
            for root, dirs, files in os.walk(os.path.join(self._path, path)):
                for dir in dirs:
                    dirname = os.path.normpath(os.path.join(root, dir)) + os.sep
                    paths.append(dirname.encode('utf8'))
                if recursive:
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                else:
                    dirs[:] = []
                for file in files:
                    filename = os.path.normpath(os.path.join(root, file))
                    paths.append(filename.encode('utf8'))

        paths = list(map(lambda x: x[len(prefix) + 1:], paths))
        paths.sort()
        return paths

    def isdir(self, path, version='HEAD'):
        if version:
            try:
                result = subprocess.check_output(['git', '-C', self.path,
                    'ls-tree', '-r', '--name-only', version, '--', path],
                    stderr=subprocess.DEVNULL)
                return result.rstrip().split(b'\n')[0].decode('utf8') != path
            except subprocess.CalledProcessError:
                return False
            except:
                return False
        else:
            return os.path.isdir(os.path.join(self._path, path))