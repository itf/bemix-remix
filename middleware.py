from settings import CERTIFICATE_URL, SSL_URL
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseForbidden
import bemix.security
from security import CertificateRequired, SslRequired

class CertificateMiddleware(object):
    def process_request(self, request):
        request.has_certificate = False
        request.certificate_email = None

        if 'SSL_CLIENT_S_DN' not in request.META:
            return

        ssl_info = dict([j.split('=', 1) for j in request.META['SSL_CLIENT_S_DN'].split('/')[1:]]) 
        if 'emailAddress' not in ssl_info:
            return False

        request.has_certificate = True
        request.certificate_email = ssl_info['emailAddress']

    def process_exception(self, request, exception):
        if isinstance(exception, CertificateRequired):
            return HttpResponseRedirect(CERTIFICATE_URL + request.get_full_path())
        elif isinstance(exception, SslRequired):
            return HttpResponseRedirect(SSL_URL + request.get_full_path())
        else:
            return None

