from django.conf import settings
from django.conf.urls import patterns
from django.conf.urls.static import static
from django.views.generic import TemplateView
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
#    (r'^$', 'views.search'),
    (r'^crossdomain.xml$', 'views.crossdomain_hack'),
    (r'^ajax_search$', 'views.ajax_search'),
    (r'^browse/(?P<folder>.*)$', 'views.browse'),
    (r'^download/(?P<path>.*)$', 'views.download'),
    (r'^$', TemplateView.as_view(template_name="home.html")),
    (r'^remix/$', 'remix.views.index'),
    (r'^timix/$', 'remix.views.timix'),
    (r'^gmix/$', 'remix.view.gmix'),
    (r'^remix/ajax_search$', 'remix.views.ajax_search'),
    (r'^remix/(?P<player_name>[\w-]*)/enqueue/(?P<song_id>.*)$', 'remix.views.enqueue'),
    (r'^remix/(?P<player_name>[\w-]*)/enqueue_youtube/(?P<youtube_url>.*)$', 'remix.views.enqueue_youtube'),
    (r'^remix/(?P<player_name>[\w-]*)/dequeue/(?P<position>.*)$', 'remix.views.dequeue'),
    (r'^remix/(?P<player_name>[\w-]*)/requeue/(?P<new_positions>.*)$', 'remix.views.requeue'),
    (r'^remix/(?P<player_name>[\w-]*)/info', 'remix.views.info'),
    (r'^remix/(?P<player_name>[\w-]*)/command/(?P<command>.*)$', 'remix.views.command'),
    (r'^remix/preferences/$', 'remix.views.preferences'),
    (r'^remix_player/tick$', 'remix.views.player_tick'),
    (r'^remix_player/get/(?P<song_id>.*)$', 'remix.views.player_get'),

    (r'^remix/playlist/(?P<playlist_name>.*)/from/(?P<player_name>[\w-]*)$', 'remix.playlist_views.playlist_from_player'),
    (r'^remix/playlist/(?P<playlist_name>.*)/play/(?P<player_name>[\w-]*)$', 'remix.playlist_views.playlist_to_player'),
    (r'^remix/playlist/(?P<playlist_name>.*)/summary$', 'remix.playlist_views.summary'),
    (r'^remix/playlists/list$', 'remix.playlist_views.list_playlists'),
    (r'^remix/playlist/add_song/(?P<playlist_id>.*)$', 'remix.playlist_views.playlist_add_song'),
    (r'^remix/playlist/delete_song/(?P<playlist_id>.*)$', 'remix.playlist_views.playlist_delete_song'),
    (r'^remix/playlist/rename/(?P<playlist_id>.*)$', 'remix.playlist_views.playlist_rename'),
    (r'^remix/playlist/reorder/(?P<playlist_id>.*)$', 'remix.playlist_views.playlist_reorder'),
    (r'^remix/playlist/enqueue/(?P<playlist_id>.*)$', 'remix.playlist_views.playlist_enqueue'),
    (r'^remix/playlist/enqueue_replace/(?P<playlist_id>.*)$', 'remix.playlist_views.playlist_enque_replace'),

    (r'^remix/get_album_art/$', 'remix.views.get_album_art'),


    (r'^uploader/$', 'uploader.views.upload'),
    (r'^uploader/do_upload/$', 'uploader.views.do_upload'),
    (r'^uploader/tag_file/$', 'uploader.views.tag_file'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
