import os, tempfile, zipfile
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

def NginxFileResponse(path):
    response = HttpResponse()
    response['Content-Type'] = '' # let nginx determine the correct content type
    print path
    response['X-Accel-Redirect'] = path
    return response

def FakeNginxFileResponse(path):
    """
    Send a file through Django without loading the whole file into
    memory at once. The FileWrapper will turn the file object into an
    iterator for chunks of 8KB.
    """
    # filename = __file__ # Select your file here.
    wrapper = FileWrapper(file(path))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(path)
    return response
