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