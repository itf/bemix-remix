import os, re, time

from bson.objectid import ObjectId
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.core.exceptions import PermissionDenied
from pymongo import *

from nginx import NginxFileResponse
from search import mongo_words_query
from security import require_known_user

# JELLE

db = Connection().bemix # temporary unclassiness

@require_known_user
def search(request):
    return render_to_response('index.html')

@require_known_user
def ajax_search(request):
    query = request.GET['query']
    results = _search(query)

    return render_to_response('results.html', {'results': results})

@require_known_user
def browse(request, folder):
    files = list(db.files.find({'folder': folder}, limit=1000))
    files.sort(key=lambda f: f['path'])

    crumbs = [{'path': '', 'name': 'root'}]
    if folder != '':
        cur = ''
        for part in folder.split('/'):
            cur += part
            crumbs.append({'path': cur, 'name': part})
            cur += '/'

    return render_to_response('browse.html', {'folder': folder, 'files': files, 'crumbs': crumbs})

def _search(query):
    if query == '':
        return []

    results = list(db.files.find({'words' : mongo_words_query(query)}, limit=200))
    results.sort(key=lambda f: f['path'])
    return results

@require_known_user
def download(request, path):
    file = db.files.find_one({'path': path})

    return NginxFileResponse('/protected/' + file['path'])

def crossdomain_hack(request):
    return HttpResponse('''
<?xml version="1.0"?>
<!DOCTYPE cross-domain-policy SYSTEM "http://www.adobe.com/xml/dtds/cross-domain-policy.dtd">
<cross-domain-policy>
  <allow-access-from domain="*" />

</cross-domain-policy>''')

