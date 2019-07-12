import os
import subprocess


class Repository:
    def __init__(self, path):
        self.path = path
        if not os.path.exists(os.path.join(self.path, '.git')):
            os.makedirs(self.path, exist_ok=True)
            subprocess.check_call(['git', '-C', self.path, 'init'])

    def file_exists(self, path):
        try:
            result = subprocess.check_output(['git', '-C', self.path, 
                'cat-file', '-e', 'master:{}'.format(path)])
        except subprocess.CalledProcessError:
            return False
        return True

    def timestamp(self, path):
        try:
            result = subprocess.check_output(['git', '-C', self.path, 'log',
                '--pretty=format:%at', '-n', '1', '--', path])
        except subprocess.CalledProcessError:
            return 0
        return int(result)

    def cat(self, path):
        try:
            result = subprocess.check_output(['git', '-C', self.path, 'cat-file',
                '-p', 'master:' + path])
        except subprocess.CalledProcessError:
            return ''
        return result.decode('utf8')

    def is_unknown(self, path):
        result = subprocess.check_output(['git', '-C', self.path, 'status',
            '--porcelain', '--', path])
        if not result:
            return False
        result = result.decode('utf8').strip()
        if os.path.isdir(path) and not path.endswith('/'):
            path += '/'
        print(result)
        if result[:2] == '??' and result[3:] == path:
            return True
        return False

    def is_dirty(self, path):
        result = subprocess.check_output(['git', '-C', self.path, 'status',
            '--porcelain', '--', path])
        if not result:
            return False
        result = result.decode('utf8')
        for line in result.split():
            if line.startswith(('M', ' M', '??')):
                return True
        return False

    def get_info(self, path):
        result = subprocess.check_output(['git', '-C', self.path, 'status',
            '--porcelain', '--', path])
        if not result:
            return {
                'in_index': False,
                'modified': False,
            }
        result = result.decode('utf8')
        X, Y = result[:2]
        return {
            'in_index': X not in ['A'],
            'modified': True,
        }
    
    def checkout(self, path):
        subprocess.check_call(['git', '-C', self.path, 'checkout', 'HEAD', '--', path])

    def move(self, src, dst):
        subprocess.check_call(['git', '-C', self.path, 'mv', src, dst])

    def add(self, path):
        subprocess.check_call(['git', '-C', self.path, 'add', path])
    
    def commit(self):
        subprocess.check_call(['git', '-C', self.path, 'commit', '-q',
            '--allow-empty-message', '-m', ''])