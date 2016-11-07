from fabric.api import *

def pack():
    local('tar czf /tmp/bemix.tgz .', capture=False)

def deploy():
    pack()
    put('/tmp/bemix.tgz', '/tmp/')
    with cd('~/bemix/'):
        run('mv settings.py settings.py.bak')
        run('tar xzf /tmp/bemix.tgz')
        run('mv settings.py.bak settings.py')

