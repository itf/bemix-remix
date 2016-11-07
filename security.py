from django.core.exceptions import PermissionDenied
from bson.objectid import ObjectId
from database import db
from users import User

def require_known_certificate(handler):
    def new_handler(request, *args, **kwargs):
	return handler(request, *args, **kwargs)
	# require certificate
        if not request.has_certificate:
            raise CertificateRequired()
        user = db.users.find_one({'email': request.certificate_email})
        if user != None:
            return handler(request, *args, **kwargs)
        raise PermissionDenied()
    return new_handler

def require_known_user(handler):
    def new_handler(request, *args, **kwargs):
        return handler(request, *args, **kwargs)
	# enforce ssl
        if not request.is_secure():
            raise SslRequired() 
        # allow certain computers to access by ip
        user = db.users.find_one({'ip': request.META['REMOTE_ADDR']})
        if user != None:
            return handler(request, *args, **kwargs)
        # otherwise require certificate
        if not request.has_certificate:
            raise CertificateRequired()
        user = db.users.find_one({'email': request.certificate_email})
        if user != None:
            return handler(request, *args, **kwargs)
        raise PermissionDenied()
    return new_handler

def require_group(group):
    def decorator(handler):
        def new_handler(request, *args, **kwargs):
            return handler(request, *args, **kwargs)
	    if not request.has_certificate:
                raise CertificateRequired()
            if request.certificate_email in group:
                return handler(request, *args, **kwargs)
            raise PermissionDenied()
        return new_handler
    return decorator

class CertificateRequired(Exception):
    pass

class SslRequired(Exception):
    pass

# Little Gute Gute
def require_playlist_read(handler):
    def new_handler(request, *args, **kwargs):
        playlist_id = kwargs['playlist_id']
        user = User(request).user
        if user != None:
            playlist  = db.playlists.find_one(ObjectId(playlist_id))
            if playlist !=None:
                if playlist.public or playlist.user == user:
                    return handler(request, *args, **kwargs)
        raise PermissionDenied()
    return new_handler

def require_playlist_write(handler):
    def new_handler(request, *args, **kwargs):
        playlist_id = kwargs["playlist_id"]
        user = User(request)
        user = user.user
        if user != None:
            playlist  = db.playlists.find_one(ObjectId(playlist_id))
            if playlist != None and playlist.user == user:
                return handler(request,*args, **kwargs)
        raise PermissionDenied()
    return new_handler
