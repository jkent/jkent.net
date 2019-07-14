from io import BytesIO
import os
import subprocess


class Repository:
    def __init__(self, path):
        self._path = path
        if not os.path.exists(os.path.join(self._path, '.git')):
            os.makedirs(self._path, exist_ok=True)
            subprocess.check_call(['git', '-C', self._path, 'init'])

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
        if version == None:
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

    def timestamp(self, path, version='HEAD'):
        try:
            result = subprocess.check_output(['git', '-C', self._path, 'log',
                '--pretty=format:%at', '-n1', '--', path])
        except subprocess.CalledProcessError:
            return 0
        return int(result)

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

    def log(self, path='.', version='HEAD', num=None):
        try:
            if not num:
                result = subprocess.check_output(['git', '-C', self.path, 'log',
                    '--pretty=format:%H', version, '--', path], 
                    stderr=subprocess.DEVNULL)
            else:
                result = subprocess.check_output(['git', '-C', self.path, 'log',
                    '-n{}'.format(num), '--pretty=format:%H', version, '--',
                    path], stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            return None

        result = result.rstrip()
        if num == 1:
            return result.decode('utf8')
        return map(lambda x: x.decode('utf8'), result.split('\n'))

    def list(self, path='.', version='master', recursive=False):
        if recursive:
            result = subprocess.check_output(['git', '-C', self.path, 'ls-tree',
                '-r', '--name-only', version, '--', path])
        else:
            result = subprocess.check_output(['git', '-C', self.path, 'ls-tree',
                '--name-only', version, '--', path])
        return result.rstrip().split('\n')


    def list(self, path, version='HEAD', recursive=False):
        if version:
            prefix = os.path.dirname(path)
            if recursive:
                result = subprocess.check_output(['git', '-C', self.path,
                    'ls-tree', '-r', '--name-only', '--directory', version, '--', path])
            else:
                result = subprocess.check_output(['git', '-C', self.path,
                    'ls-tree', '--name-only', '--full-name', version, '--', path])
            paths = result.rstrip().split(b'\n')
        else:
            print('here!')
            prefix = os.path.dirname(os.path.join(self._path, path))
            paths = []
            for root, dirs, files in os.walk(os.path.join(self._path, path)):
                for dir in dirs:
                    dirname = os.path.normpath(os.path.join(root, dir))
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