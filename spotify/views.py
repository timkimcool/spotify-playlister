from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView
from django.http import JsonResponse
from .scripts.artist import get_artist_info, get_artist_tracks, get_similar_tracks_track, get_similar_tracks_artist
from .scripts.user import get_user_summary, get_user_playlists
from .scripts.user_top import get_top_track_info, get_top_artist_info
import spotipy
from spotipy import oauth2
from spotipy.cache_handler import DjangoSessionCacheHandler
from environs import Env
env = Env()
env.read_env()

import logging
logger = logging.getLogger('testlogger')
logger.info('This is a simple log message')

SPOTIPY_CLIENT_ID = env.str("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = env.str("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = env.str("SPOTIPY_REDIRECT_URI")
scope = 'user-top-read playlist-modify-private playlist-modify-public playlist-read-private'

def get_context_var(request):
    context = {
        'playlists': request.session.get('playlists', ''),
        'playlist_tracks': request.session.get('tracks', []),
        'track_ids': request.session.get('track_ids', []),
        'id': request.session.get('id', "timkimcool"),
        'image': request.session.get('image', ''),
        'selected_playlist_name': request.session.get('selected_playlist_name', ""),
        'selected_playlist_id': request.session.get('selected_playlist_id', ""),
    }
    return context
             
class HomeView(TemplateView):
    template_name = 'base.html'
    def get(self, request):
        request.session['first'] = True
        return render(request, 'base.html')

class TopTracksView(TemplateView):
    def get(self, request):
        sp = spotipy.Spotify(request.session['access'])
        # logger.error(request.session.items())
        context = {
            'long': get_top_track_info(sp, 'long_term'),
            'medium': get_top_track_info(sp, 'medium_term'),
            'short': get_top_track_info(sp, 'short_term'),
        } | get_context_var(request)
        return render(request, 'user-top-tracks.html', context)
            

class TopArtistsView(TemplateView):
    def get(self, request):
        sp = spotipy.Spotify(request.session['access'])
        context = {
            'long': get_top_artist_info(sp, 'long_term'),
            'medium': get_top_artist_info(sp, 'medium_term'),
            'short': get_top_artist_info(sp, 'short_term'),
        } | (get_context_var(request))

        return render(request, 'user-top-artists.html', context)

class ArtistTrackView(TemplateView):
    def get(self, request, *args, **kwargs):
        sp = spotipy.Spotify(request.session['access'])
        artist_info = get_artist_tracks(sp, kwargs['id'])
        context = {
            'tracks': artist_info['tracks'], 
            'related_artists': artist_info['artists'], 
            'name': kwargs['name'],

        } | get_context_var(request)
        return render(request, 'artist-tracks.html', context)

class SimilarTrackTrackView(TemplateView):
    def get(self, request, *args, **kwargs):
        sp = spotipy.Spotify(request.session['access'])
        track_info = get_similar_tracks_track(sp, kwargs['track_id'], request.session['user_features'])['tracks']
        context = {
            'tracks': track_info, 
            'name': kwargs['name'],
        } | get_context_var(request)
        return render(request, 'similar-tracks.html', context)

class SimilarTrackArtistView(TemplateView):
    def get(self, request, *args, **kwargs):
        sp = spotipy.Spotify(request.session['access'])
        track_info = get_similar_tracks_artist(sp, kwargs['artist_id'], request.session['user_features'])['tracks']

        context = {
            'tracks': track_info, 
            'name': kwargs['name'],
        } | get_context_var(request)
        return render(request, context)

class ArtistView(TemplateView):
    def post(self, request, *args, **kwargs):
        sp = spotipy.Spotify(request.session['access'])
        artist_str = request.POST.get('artist')
        if 'artist' in artist_str:
            artist_id = artist_str[artist_str.index('/artist/') + 8 : artist_str.index('?')]
        else:
            artist_id = artist_str
        artist_info = get_artist_info(sp, artist_id)

        context = {
            'artist': artist_info,
        } | get_context_var(request)
        return render(request, 'artist-info.html', context)

class CreatePlaylistView(TemplateView):
    def get(self, request, **kwargs):
        sp = spotipy.Spotify(request.session['access'])
        id = request.session['id']
        name = request.GET.get('name')
        playlist = sp.user_playlist_create(id, name, description="Playlist created on Spotify Profile")
        request.session['playlists'].append(playlist['id'])
        return render(request, 'sign-in.html', {'id': playlist['id']})

class AddToPlaylistView(TemplateView):
    def get(self, request):
        sp = spotipy.Spotify(request.session['access'])
        playlist_id = request.GET.get('playlist_id')
        track_id = request.GET.get('track_id')
        sp.playlist_add_items(playlist_id, [track_id])
        # request.session['track_ids'] = []
        # request.session['tracks'] = []
        return render(request, 'sign-in.html', {})

# class RemoveTrackView(TemplateView):
#     def get(self, request):
#         logger.error(request.GET.get('id'))
#         logger.error(request.session['track_ids'])
#         logger.error(len(request.session['tracks']))
#         track_id = request.GET.get('id')
#         request.session['track_ids'].remove(track_id)
#         for i, track in enumerate(request.session['tracks']):
#             if track['id'] == track_id:
#                 index = i
#                 break
#         request.session['tracks'].pop(index)
#         request.session.modified = True
#         return render(request, 'sign-in.html', {})

class SignInView(TemplateView):
    def get(self, request, **kwargs):
        cache_handler = DjangoSessionCacheHandler(request)
        sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=scope, cache_handler=cache_handler)
        if not request.session.get('access', ""):
            if request.GET.get('code'):
                token_info = sp_oauth.get_access_token(request.GET.get('code'))
                request.session['access'] = token_info["access_token"]
            else:
                auth_url = sp_oauth.get_authorize_url()
                return HttpResponseRedirect(auth_url)
        sp = spotipy.Spotify(auth=request.session['access'])
        try:
            results = get_user_summary(sp)
        except:
            cache_handler = DjangoSessionCacheHandler(request)
            sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=scope, cache_handler=cache_handler)
            auth_url = sp_oauth.get_authorize_url()
            return HttpResponseRedirect(auth_url)
        playlists = get_user_playlists(sp)
        if not request.session.get('image', ""):
            request.session['id'] = results['id']
            request.session['image'] = results['image']
            request.session['playlists'] = playlists
            request.session['user_features'] = results['user_features']
            request.session['tracks'] = ""
        results = get_user_summary(sp)
        playlists = get_user_playlists(sp)
        data = {
            'labels': ','.join([key for key in results['user_features'] if key != 'tempo']),
            'data': ','.join([str(results['user_features'][key][0]) for key in results['user_features'] if key != 'tempo']),
        }
        context = {
            'results': results, 
            'data': data, 
            'playlists': playlists 
        } | get_context_var(request)
        
        return render(request, 'sign-in.html', context)

class SelectedPlaylistView(TemplateView):
    def get(self, request, **kwargs):
        request.session['selected_playlist_id'] = request.GET.get('id')
        request.session['selected_playlist_name'] = request.GET.get('name')
        return JsonResponse({}, status=200)

class FirstView(TemplateView):
        def get(self, request, **kwargs):
            request.session['first'] = False
            return JsonResponse({}, status=200)

# class AddToListView(TemplateView):
#     def get(self, request, *args, **kwargs):
#         logger.error("START")
#         logger.error(request.session.get('track_ids', "fail"))
#         track = {}
#         track['name'] = request.GET.get('name')
#         track['image'] = request.GET.get('image')
#         track['artists'] = request.GET.get('artists')
#         track['id'] = request.GET.get('id')
#         if not request.session.get('track_ids', ""):
#             logger.error("if" + track['id'])
#             request.session['tracks'] = [track]
#             request.session['track_ids'] = [track['id']]
#         elif track['id'] not in request.session['track_ids']:
#             logger.error("else" + track['id'])
#             request.session['tracks'].append(track)
#             request.session['track_ids'].append(track['id'])
#         request.session.modified = True
#         logger.error("END")
#         logger.error(request.session.get('track_ids', "fail"))
#         return JsonResponse({"id": track['id']}, status=200)
