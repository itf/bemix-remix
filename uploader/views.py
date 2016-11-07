import json
import os
import shutil
from indexer.organizer import Organizer
from django.conf import settings
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django import forms
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.mp3 import HeaderNotFoundError

class TagForm(forms.Form):
    full_filename = forms.CharField(max_length=1000, required=True,min_length=5)
    artist = forms.CharField(max_length=1000,required=True,min_length=2)
    album = forms.CharField(max_length=1000,required=True,min_length=2)
    title = forms.CharField(max_length=1000,required=True,min_length=2)

@csrf_exempt
def do_upload(request):
    if request.method == 'POST':
        text = ""
        for f in request.FILES:
            text += ": " + f
        file = request.FILES['files[]']
        results = handle_uploaded_file(file)
        return HttpResponse(json.dumps(results))
    else:
        raise Http404()

def handle_uploaded_file(file):
    full_filename = file.temporary_file_path()
    filename = file.name
    (basename, ext) = os.path.splitext(filename)
    if ext == ".mp3":
        try:
            audio = MP3(full_filename, ID3=EasyID3)
            try:
                title = audio['title'][0]
            except Exception:
                title = ""  
            try:
                album = audio['album'][0]
            except Exception:
                album = ""
            try:
                artist = audio['artist'][0]
            except Exception:
                artist = ""
            try:
                tracknumber = audio['tracknumber'][0]
            except Exception:
                tracknumber = ""
            try:
                length = audio.info.length
            except Exception:
                length = 0.0
    
            processing_dir = os.path.join(settings.DATA_ROOT, 'Processing')
            if not os.path.exists(processing_dir):
                os.makedirs(processing_dir)
            target = os.path.join(processing_dir, os.path.basename(full_filename) + ".mp3")
            shutil.move(full_filename, target)
            
            return {"title": title,
                    "album": album,
                    "artist": artist,
                    "tracknumber": tracknumber,
                    "length": length,
                    "success": True,
                    "full_filename": target}
        except Exception as e:
            return {"success" : False,
                    "exception" : str(e)}
    else:
        return {"success": False}

@csrf_exempt
def tag_file(request):
    print os.path.join(settings.DATA_ROOT, 'ProcessedMusic')
    if request.method == 'POST':
        form = TagForm(request.POST)
        print "form is valid? " + str(form.is_valid())
        if form.is_valid():
            print "Valid Form"
            artist  = form.cleaned_data['artist']
            album = form.cleaned_data['album']
            title = form.cleaned_data['title']
            full_filename = form.cleaned_data['full_filename']            
            try:
                audio = EasyID3(full_filename)
                audio['title'] = unicode(title)
                audio['artist'] = unicode(artist)
                audio['album'] = unicode(album)
                audio.save()
                o = Organizer()
                o.process_file(full_filename, os.path.join(settings.DATA_ROOT, 'ProcessedMusic'))
            except Exception as e:
                raise
                return HttpResponse(json.dumps({"success": False, "exception": str(e)}))
            
            return HttpResponse(json.dumps({"success": True}))
        else:
            return HttpResponse(json.dumps({"success": False, "error": "invalid form"}))
    return HttpResponse(json.dumps({"success" : False, "error": "GET"}))

@csrf_exempt
def upload(request):
    return render_to_response('uploader/upload.html')
