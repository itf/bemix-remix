from subprocess import Popen, PIPE
from pymongo import ASCENDING
from database import db

allowed_ips = [u'18.238.0.240',  # donlanes
                u'18.238.1.188', # coldwar
                u'18.238.1.169'] # classy

def load_users():
    db.users.drop()
    db.users.ensure_index([('email', ASCENDING)])
    db.users.ensure_index([('ip', ASCENDING)])
    output = Popen(['blanche', 'fashion', '-u', '-r', '-noauth'], stdout=PIPE).communicate()[0].strip().split('\n')
    for username in output:
        new_user = db.users.User()
        new_user.email = unicode(username + '@MIT.EDU')
        new_user.preferences = {}
        db.users.save(new_user)
        print "Added %s" % username
    for ip in allowed_ips:
        new_user = db.user.User()
        new_user.ip = ip
        new_user.preferences = {}
        db.users.save(new_user)
        print "Added %s" % ip

if __name__ == '__main__':
    load_users()
