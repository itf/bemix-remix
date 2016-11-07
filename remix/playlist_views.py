import json

from bson.objectid import ObjectId
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from database import db

from search import mongo_words_query
from security import require_group, require_known_user,require_playlist_read,require_playlist_write

from nginx import NginxFileResponse

from player import Player

from remix.views import get_player, save_player, get_or_create_player, get_song, JsonResponse

from users import User

def get_playlist(playlist_name):
    mongo_object = db.playlists.Playlist.find_one({'name': playlist_name})
    if mongo_object != None:
        return mongo_object
    else:
        raise Http404()

def get_or_create_playlist(playlist_name):
    mongo_object = db.playlists.Playlist.find_one({'name': playlist_name})
    if mongo_object != None:
        return mongo_object
    else:
        return db.playlists.Playlist({
            'name': playlist_name,
            'songs': [],
            'public': True,
        })

def playlist_from_player(request, playlist_name, player_name):
    playlist = get_or_create_playlist(playlist_name)
    player = get_player(player_name)
    playlist.songs = player.queue
    playlist.save()
    return JsonResponse({'success': True})

def playlist_to_player(request, playlist_name, player_name):
    playlist = get_playlist(playlist_name)
    player = get_player(player_name)
    for song in playlist.songs:
        player.enqueue(song)
    save_player(player)
    return JsonResponse({'success': True})

def list_playlists(request):
    return JsonResponse({
        'playlists': [pl.name for pl in db.playlists.Playlist.find()],
    })

def summary(request, playlist_name):
    playlist = get_playlist(playlist_name)
    return JsonResponse({
        'length': len(playlist.songs),
        'names': [db.songs.Song.find_one(song).title for song in playlist.songs],
    })

### Everything below this line is not really in use.

@require_playlist_write
def playlist_add_song(request,playlist_id):
    try:
        playlist = db.playlist.find_one(ObjectId(playlist_id))
        song_id = request.POST['song_id']
        song = get_song(song_id)
        playlist.songs.append(song)
        playlist.save()
        return JsonResponse({'success': True, 'playlist': playlist})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_playlist_write
def playlist_delete_song(request,playlist_id):
    try:
        playlist = db.playlist.find_one(ObjectId(playlist_id))
        song_id = request.POST['song_id']
        song = get_song(song_id)
        playlist.songs.remove(song)
        playlist.save()
        return JsonResponse({'success': True, 'playlist': playlist})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_playlist_write
def playlist_rename(request,playlist_id):
    try:
        playlist = db.playlist.find_one(ObjectId(playlist_id))
        name = request.POST['name']
        playlist.name = name
        playlist.save()
        return JsonResponse({'success': True, 'playlist': playlist})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_playlist_write
def playlist_reorder(request,playlist_id):
    return JsonResponse({"success": True})

@require_playlist_read
def playlist_enqueue(request,playlist_id):
    playlist = db.playlist.find_one(ObjectId(playlist_id))
    if playlist != None:
        player = get_player(player_name)
        songs = playlist.songs
        for song in songs:
            player.enqueue(ObjectId(song.id))
        save_player(player)
        return JsonResponse({'success': True, 'playlist': playlist})
    else:
        return JsonResponse({'success': False})

@require_playlist_read
def playlist_enqueue_replace(request,playlist_id):
    playlist = db.playlist.find_one(ObjectId(playlist_id))
    if playlist != None:
        player = get_player(player_name)
        player.queue = []
        songs = playlist.songs
        for song in songs:
            player.enqueue(ObjectId(song.id))
        save_player(player)
        return JsonResponse({'success': True, 'playlist': playlist})
    else:
        return JsonResponse({'success': False})

def view_all(request):
    # user = User(request).user
    # playlists = db.playlists.find({'$or' : [{'creator': user}, {'public': True}]}) 
    playlists = db.playlists.find({'public': True})
    return JsonResponse({'success': True, 'playlists': list(playlists)})
