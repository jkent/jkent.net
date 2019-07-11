import os
import subprocess


class GitRepo:
    def __init__(self, path):
        self.path = path
        if not os.path.exists(os.path.join(self.path, '.git')):
            subprocess.check_call(['git', '-C', self.path, 'init'])

    def get_timestamp(self, path):
        result = subprocess.check_output(['git', '-C', self.path, 'log',
            '--pretty=format:%at', '-n', '1', '--', path])
        if not result:
            return None
        return int(result)

    def get_index(self, path):
        try:
            result = subprocess.check_output(['git', '-C', self.path, 'cat-file',
                '-p', 'master:' + path])
        except subprocess.CalledProcessError:
            return None
        return result.decode('utf8')

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
        subprocess.check_call(['git', '-C', self.path, 'checkout', '--', path])

    def move(self, src, dst):
        subprocess.check_call(['git', '-C', self.path, 'mv', src, dst])

    def add(self, path):
        subprocess.check_call(['git', '-C', self.path, 'add', path])
    
    def commit(self):
        subprocess.check_call(['git', '-C', self.path, 'commit', '-q',
            '--allow-empty-message', '-m', ''])