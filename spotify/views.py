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

class HomeView(TemplateView):
    template_name = 'base.html'
    def get(self, request, **kwargs):
        request.session.flush()
        request.session['tracks'] = []
        request.session['track_ids'] = []
        return render(request, 'base.html')

class TopTracksView(TemplateView):
    def get(self, request, *args, **kwargs):
        sp = spotipy.Spotify(request.session['access'])
        results_long = get_top_track_info(sp, 'long_term')
        results_med = get_top_track_info(sp, 'medium_term')
        results_short = get_top_track_info(sp, 'short_term')
        return render(request, 'user-top-tracks.html', {'long': results_long, 'medium': results_med, 'short': results_short, 
            'playlists': request.session['playlists'], 'playlist_tracks': request.session['tracks'],
            'id': request.session['user_id'], 'image': request.session['image'] })

class TopArtistsView(TemplateView):
    def get(self, request, *args, **kwargs):
        sp = spotipy.Spotify(request.session['access'])
        results_long = get_top_artist_info(sp, 'long_term')
        results_med = get_top_artist_info(sp, 'medium_term')
        results_short = get_top_artist_info(sp, 'short_term')
        return render(request, 'user-top-artists.html', {'long': results_long, 'medium': results_med, 
            'short': results_short, 'playlists':request.session['playlists'], 'playlist_tracks': request.session['tracks'],
            'id': request.session['user_id'], 'image': request.session['image'] })

class ArtistTrackView(TemplateView):
    def get(self, request, *args, **kwargs):
        sp = spotipy.Spotify(request.session['access'])
        artist_info = get_artist_tracks(sp, kwargs['id'])
        return render(request, 'artist-tracks.html', {'tracks': artist_info['tracks'], 'related_artists': artist_info['artists'], 
            'name': kwargs['name'], 'playlists':request.session['playlists'], 'playlist_tracks': request.session['tracks'],
            'id': request.session['user_id'], 'image': request.session['image'] })

class SimilarTrackTrackView(TemplateView):
    def get(self, request, *args, **kwargs):
        sp = spotipy.Spotify(request.session['access'])
        track_info = get_similar_tracks_track(sp, kwargs['track_id'], request.session['user_features'])['tracks']
        return render(request, 'similar-tracks.html', {'tracks': track_info, 'name': kwargs['name'],
            'playlists':request.session['playlists'], 'playlist_tracks': request.session['tracks'],
            'id': request.session['user_id'], 'image': request.session['image'] })

class SimilarTrackArtistView(TemplateView):
    def get(self, request, *args, **kwargs):
        sp = spotipy.Spotify(request.session['access'])
        track_info = get_similar_tracks_artist(sp, kwargs['artist_id'], request.session['user_features'])['tracks']
        return render(request, 'similar-tracks.html', {'tracks': track_info, 'name': kwargs['name'], 
            'playlists':request.session['playlists'], 'playlist_tracks': request.session['tracks'],
            'id': request.session['user_id'], 'image': request.session['image'] })

class ArtistView(TemplateView):
    def post(self, request, *args, **kwargs):
        # create a form instance and populate it with data from the request:
        sp = spotipy.Spotify(request.session['access'])
        artist_str = request.POST.get('artist')
        if 'artist' in artist_str:
            artist_id = artist_str[artist_str.index('/artist/') + 8 : artist_str.index('?')]
        else:
            artist_id = artist_str
        artist_info = get_artist_info(sp, artist_id)
        return render(request, 'artist-info.html', {'artist': artist_info, 'id': request.session['user_id'], 'image': request.session['image']})

class CreatePlaylistView(TemplateView):
    def get(self, request, **kwargs):
        sp = spotipy.Spotify(request.session['access'])
        id = request.session['user_id']
        name = request.GET.get('name')
        playlist = sp.user_playlist_create(id, name, description="Playlist created on Spotify Profile")
        return render(request, 'sign-in.html', {'id': playlist['id']})

class AddToPlaylistView(TemplateView):
    def get(self, request):
        sp = spotipy.Spotify(request.session['access'])
        playlist_id = request.GET.get('id')
        sp.playlist_add_items(playlist_id, request.session['track_ids'])
        request.session['track_ids'] = []
        request.session['tracks'] = []
        return render(request, 'sign-in.html', {'playlist_tracks': request.session['tracks']})

class RemoveTrackView(TemplateView):
    def get(self, request):
        track_id = request.GET.get('id')
        request.session['track_ids'].remove(track_id)
        for i, track in enumerate(request.session['tracks']):
            if track['id'] == track_id:
                index = i
        request.session['tracks'].pop(index)
        return render(request, 'sign-in.html', {})

class SignInView(TemplateView):
    def get(self, request, **kwargs):
        cache_handler = DjangoSessionCacheHandler(request)
        sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=scope, cache_handler=cache_handler)
        if request.GET.get('code'):
            token_info = sp_oauth.get_access_token(request.GET.get('code'))
        else:
            auth_url = sp_oauth.get_authorize_url()
            return HttpResponseRedirect(auth_url)
        if not request.session.get('access', ""):
            request.session['access'] = token_info["access_token"]
            sp = spotipy.Spotify(auth=request.session['access'])
            results = get_user_summary(sp)
            playlists = get_user_playlists(sp)
            request.session['user_id'] = results['user']['id']
            request.session['image'] = results['user']['image']
            request.session['playlists'] = playlists
            request.session['user_features'] = results['user_features']
            data = {
                'labels': ','.join([key for key in results['user_features'] if key != 'tempo']),
                'data': ','.join([str(results['user_features'][key][0]) for key in results['user_features'] if key != 'tempo']),
            }
        return render(request, 'sign-in.html', {'results': results, 'data': data, 'playlists': playlists, 'playlist_tracks': request.session.get('tracks', "")})

class AddToListView(TemplateView):
    def get(self, request, *args, **kwargs):
        track = {}
        track['name'] = request.GET.get('name')
        track['image'] = request.GET.get('image')
        track['artists'] = request.GET.get('artists')
        track['id'] = request.GET.get('id')
        if not request.session['track_ids']:
            request.session['tracks'] = [track]
            request.session['track_ids'] = [track['id']]
        elif track['id'] not in request.session['track_ids']:
            request.session['tracks'] = request.session['tracks'].append(track)
            request.session['track_ids'] = request.session['track_ids'].append(track['id'])
        return JsonResponse({"id": track['id']}, status=200)
