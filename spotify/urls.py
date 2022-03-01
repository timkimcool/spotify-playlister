from django.urls import path
from .views import (
    HomeView, 
    SignInView, 
    ArtistView, 
    TopTracksView, 
    TopArtistsView, 
    ArtistTrackView,
    CreatePlaylistView,
    # AddToListView,
    SimilarTrackTrackView,
    SimilarTrackArtistView,
    SelectedPlaylistView,
    AddToPlaylistView,
    FirstView,
    # RemoveTrackView,
)

urlpatterns = [
    path('sign-in/', SignInView.as_view(), name='sign-in'),
    path('artist_info/', ArtistView.as_view(), name='artist_info'),
    path('create_playlist/', CreatePlaylistView.as_view(), name='create_playlist'),
    path('add_to_playlist/', AddToPlaylistView.as_view(), name='add_to_playlist'),
    path('select_playlist/', SelectedPlaylistView.as_view(), name='select_playlist'),
    path('get_top_tracks/', TopTracksView.as_view(), name='get_top_tracks'),
    path('get_top_artists/', TopArtistsView.as_view(), name='get_top_artists'),
    path('get_top_artists/<str:id>/<str:name>/tracks/', ArtistTrackView.as_view(), name='artist_tracks'),
    path('get_similar_tracks_to_track/<str:track_id>/<path:name>/', SimilarTrackTrackView.as_view(), name='similar_tracks_track'),
    path('get_similar_tracks_to_artist/<str:artist_id>/<path:name>/', SimilarTrackArtistView.as_view(), name='similar_tracks_artist'),
    path('first/', FirstView.as_view(), name='first'),
    # path('add/', AddToListView.as_view(), name='add_playlist'),
    # path('remove/', RemoveTrackView.as_view(), name='remove_track'),
    path('', HomeView.as_view(), name='home'),
]