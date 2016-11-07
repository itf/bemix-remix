import os, time
from datetime import datetime, timedelta

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import mutagen.id3

from amazonproduct import API
import requests
import sys
import re
import json

from bson.objectid import ObjectId
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from database import db

from django.conf import settings
from django.template.defaultfilters import slugify
from search import mongo_words_query
from security import require_group, require_known_user,require_playlist_read,require_playlist_write

from nginx import NginxFileResponse, FakeNginxFileResponse

from player import Player
from users import User
from random import randint
import youtubeUtils
# BEMIX SETTINGS
SEARCH_GROUP = 'Music'
STYLES = ['blue', 'jelle']


def get_player(name):
    mongo_object = db.players.find_one({'name': name})
    if mongo_object != None:
        return Player(mongo_object=mongo_object)
    else:
        raise Http404()

def get_or_create_player(name):
    mongo_object = db.players.find_one({'name': name})
    if mongo_object != None:
        return Player(mongo_object=mongo_object)
    else:
        return Player(name=name)

def get_song(song_id):
    mongo_object = db.songs.find_one(ObjectId(song_id))
    if mongo_object != None:
        return mongo_object
    else:
        raise Http404()

def get_song_info(song):
    song_id=song["song"]
    source = song["source"]
    if (source == "local"):
        mongo_object = db.songs.find_one(ObjectId(song_id))
        if mongo_object != None:
            return mongo_object
        else:
            raise Http404()
    elif (source == "youtube"):
        return youtubeUtils.getSongFromYoutube(song_id)
    else:
        return song
        

def get_playlist(playlist_id):
    mongo_object = db.playlists.find_one(ObjectId(playlist_id))
    if mongo_object != None:
        return mongo_object
    else:
        raise Http404()

def save_player(player):
    db.players.save(player.to_mongo_dict())

def get_active_players():
    TIMEOUT_MINUTES = 10
    cutoff = datetime.now() - timedelta(seconds=TIMEOUT_MINUTES * 60)
    return db.players.find({
        '$or': [{'owner': 'sys'}, {'owner': None}],
        'last_tick': {'$gte': cutoff},
        })
    # return (db.players.find({'$or': [{'owner': 'sys'}, {'owner': None}]})
                      # .find({'last_tick': {'$gte': cutoff}}))

    # return db.players.find({'last_tick': {'$gte': cutoff}})
    # Used to be:
    # return db.players.find({'$or': [{'owner': 'sys'}, {'owner': None}]})

@require_known_user
def index(request):
    user = User(request)
    if user.type == 'email':
        local_player = get_or_create_player(user.email)
        if user.pref_true('local_public'):
            local_player.owner = 'sys'
        else:
            local_player.owner = user.full_email
        save_player(local_player)
    style = user.pref_value("style")
    if style == 0:
        style = STYLES[0]
    players = get_active_players()
    return render_to_response('remix/index.html', {'players': players, 
        'style': style, 'styles': STYLES, 'user': user, 'local_public': user.pref_true('local_public')})

@require_known_user
def timix(request):
    user = User(request)
    if user.type == 'email':
        local_player = get_or_create_player(user.email)
        if user.pref_true('local_public'):
            local_player.owner = 'sys'
        else:
            local_player.owner = user.full_email
        save_player(local_player)
    style = user.pref_value("style")
    if style == 0:
        style='blue'
    players = get_active_players()
    return render_to_response('timix/index.html', {'players': players, 
        'style': style, 'styles': STYLES, 'user': user, 'local_public': user.pref_true('local_public')})

@require_known_user
def gmix(request):
    user = User(request)
    if user.type == 'email':
        local_player = get_or_create_player(user.email)
        if user.pref_true('local_public'):
            local_player.owner = 'sys'
        else:
            local_player.owner = user.full_email
        save_player(local_player)
    style = user.pref_value("style")
    if style == 0:
        style='blue'
    players = get_active_players()
    return render_to_response('gmix/index.html', {'players': players, 
        'style': style, 'styles': STYLES, 'user': user, 'local_public': user.pref_true('local_public')})

@require_known_user
def ajax_search(request):
    query = request.GET['query']
    results = list(db.songs.find({'words' : mongo_words_query(query)}, limit=150))
    results.sort(key=lambda song: (song['album'], song['tracknumber']))
    res = []
    for r in results:
        res += [{'id': str(r['_id']), 'title': r['title'], 'album': r['album'], 'artist': r['artist']}]
    return JsonResponse({'results': res})

@require_known_user
def enqueue(request, player_name, song_id):
    player = get_player(player_name)
    player.enqueue(ObjectId(song_id))
    save_player(player)
    return HttpResponse()

def enqueue_youtube(request, player_name, youtube_url):
    player = get_player(player_name)
    player.enqueue_youtube(youtube_url)
    save_player(player)
    return HttpResponse()
    
@require_known_user
def dequeue(request, player_name, position):
    player = get_player(player_name)
    position = int(position)
    if 0 <= position < len(player.queue):
        player.dequeue(position)
    save_player(player)
    return HttpResponse()
    
@require_known_user
def requeue(request, player_name, new_positions):
    player = get_player(player_name)
    new_positions = new_positions.split(',')
    new_queue = [player.queue[0]]
    new_queue += [player.queue[int(pos)] for pos in new_positions]
    player.queue = new_queue
    save_player(player)
    return HttpResponse()

@require_known_user
def info(request, player_name):
    player = get_player(player_name)
    queue = [get_song_info(song) for song in player.queue]
    json_queue = []
    count = 0
    
    for item in queue:
        try:
            json_queue += [{'place':count, 'title':item['title'], 'artist':item['artist'], 'album':item['album']}]
        except:
            json_queue += [{'place':"", 'title':str(item), 'artist':"", 'album':""}]
        count += 1
    if len(queue) > 0:
        percent = (player.position / queue[0]['length'])*100.0
        time_at = time.strftime('%M:%S', time.gmtime(player.position))
        time_total = time.strftime('%M:%S', time.gmtime(queue[0]['length']))
    else:
        percent = 0.0
        time_at = '00:00'
        time_total = '00:00'
    
    return_data = {'volume': player.volume,
                    'state': player.state,
                    'repeat': player.repeat,
                    'time_at': time_at,
                    'time_total': time_total,
                    'percent': percent,
                    'queue': json_queue}
    return JsonResponse(return_data)

#@require_known_user
def command(request, player_name, command):
    player = get_player(player_name)

    if command == 'prev':
        player.previous_song()
    if command == 'next':
        player.next_song()
    if command == 'pause':
        if player.state == 'playing':
            player.state = 'paused'
        else:
            player.state = 'playing'
    if command == 'addrandom':
        randomNumber=randint(0,db.songs.count())
        song_id=db.songs.find().limit(-1).skip(randomNumber).next()
        player.queue.insert(0, ObjectId(song_id['_id']))
        save_player(player)
        player.state = 'playing'
    if command == 'test':
        player.repeat= player.repeat
    if command == 'volup':
        player.volume_up()
    if command == 'voldown':
        player.volume_down()
    if command == 'repeat':
        player.repeat = not player.repeat
    if command[0:6] == 'volset':
        player.volume_set(int(command[6:9]))
    
    save_player(player)
    return HttpResponse()

@csrf_exempt
@require_known_user
def preferences(request):
    user = User(request)
    info = json.loads(request.POST['json'])
    user.preferences['local_public'] = info['local_public']
    user.preferences['style'] = info['style']
    user.save_preferences()
    return HttpResponse(str(user.preferences))

def JsonResponse(response):
    return HttpResponse(json.dumps(response, indent=2))

@csrf_exempt
def player_tick(request):
    info = json.loads(request.POST['json'])
    player = get_or_create_player(info['name'])
    ret = player.tick(info)
    save_player(player)
    return JsonResponse(ret)

def player_get(request, song_id):
    song = db.songs.find_one(ObjectId(song_id))

    if settings.USE_NGINX_SONGS:
        path = os.path.join('protected', 'ProcessedMusic', song['path'])
        return NginxFileResponse(path)
    else:
        path = os.path.join(settings.DATA_ROOT, 'ProcessedMusic', song['path'])
        return FakeNginxFileResponse(path)

def get_image_from_amazon(artist, album):
    api = API(
        access_key_id="First it was fix-ed",
        secret_access_key="And then it was enabled",
        associate_tag="But now it's broke again.",
        locale="us")

    node = api.item_search('Music', ResponseGroup='Images',
            Keywords="{} {}".format(artist, album))
    url = str(node.page(1).Items.Item.LargeImage.URL)
    data = requests.get(url).content
    return data

def get_image_from_itunes(artist, album):
    url = ("https://itunes.apple.com/search?term=nevermind&entity={}+{}&limit=1"
           .format(artist, album))
    query_url = ("https://itunes.apple.com/search?term={} {}&entity=album&limit=1"
           .format(artist, album))
    res = requests.get(query_url).json()
    img_url = res['results'][0]['artworkUrl100']
    img_url = img_url.replace("100x100", "400x400")
    data = requests.get(img_url).content
    return data

def get_album_art(request):
    artist = request.GET['artist']
    album = request.GET['album']
    art = db.art.find_one({'album': album, 'artist': artist})
    art = None
    try:
        if art != None:
            file_handle = open(art['path'], 'rb')
            data = file_handle.read()
            file_handle.close()
        else:
            data = get_image_from_itunes(artist, album)
            folder = os.path.join(settings.DATA_ROOT, 'AlbumArt', slugify(artist))
            if not os.path.exists(folder):
                os.makedirs(folder)
            path = folder + os.sep + slugify(album) + '.jpg'
            with open(path, 'wb') as f:
                f.write(data)
            art = db.art.Art()
            art.album = unicode(album)
            art.artist = unicode(artist)
            art.path = unicode(path)
            art.save()
    except Exception as e:
        raise
        default = open(os.path.join(settings.DATA_ROOT, 'AlbumArt/default.jpg'), 'rb')
        data = default.read()
        default.close()
    return HttpResponse(data, mimetype='image/jpg')
