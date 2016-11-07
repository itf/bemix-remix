from mongokit import *
import datetime

connection = Connection()

@connection.register
class User(Document):
    structure = {
        'email': unicode,
        'ip': unicode,
        'preferences': dict
    }
    use_dot_notation = True

@connection.register
class Song(Document):
    structure = {
        'title': unicode,
        'album': unicode,
        'artist': unicode,
        'tracknumber': unicode,
        'length': float,
        'path': unicode,
	    'duplicate': int,
	    'words': [unicode],
        'uploader': User
    }
    use_dot_notation = True

@connection.register
class File(Document):
    structure = {
        'path': unicode,
        'directory': unicode,
        'mimetype': unicode,
        'words': [unicode],
        'modified': datetime.datetime
    }
    use_dot_notation = True

@connection.register
class Directory(Document):
    structure = {
        'path': unicode
    }
    use_dot_notation = True

@connection.register
class Playlist(Document):
    structure = {
        'name': unicode,
        'songs': [Song],
        'creator': User,
        'public': bool
    }
    use_dot_notation = True

@connection.register
class Player(Document):
    structure = {
        'name': unicode,
        'owner': User,
        'state': unicode,
        'queue': [Song],
        'history': [Song],
        'volume': int,
        'position': float,
        'last_tick': datetime.datetime,
        'repeat': bool,
        'queue_type': unicode,
        'playlist': Playlist,
        'query': unicode,
        'artist': unicode,
        'album': unicode,
        'playing': Song
    }
    use_dot_notation = True

@connection.register
class Art(Document):
    structure = {
        'artist': unicode,
        'album': unicode,
        'path': unicode

    }
    use_dot_notation = True

db = connection.bemix
