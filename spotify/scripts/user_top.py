from typing import List, Dict

def get_top_track_info(sp, range):
    tracks = []
    track_ids = []
    top_tracks = sp.current_user_top_tracks(time_range=range, limit=50)['items']
    for track in top_tracks:
        track_info = {}
        track_info['image'] = track['album']['images'][-1] if track['album']['images'] else False
        track_info['name'] = track['name']
        track_info['date'] = track['album']['release_date']
        track_info['album_name'] = track['album']['name']
        track_info['artists'] = ", ".join([artist['name'] for artist in track['artists']])
        track_info['popularity'] = track['popularity']
        track_info['link'] = track['external_urls']['spotify']
        track_info['preview'] = track['preview_url']
        track_info['id'] = track['id']
        track_ids.append(track['id'])
        tracks.append(track_info)
    return tracks

def get_top_artist_info(sp, range):
    artists = []
    top_artists = sp.current_user_top_artists(time_range=range, limit=50)['items']
    for artist in top_artists:
        artist_info = {}
        artist_info['image'] = artist['images'][-1] if artist['images'] else False
        artist_info['name'] = artist['name']
        artist_info['followers'] = artist['followers']['total']
        artist_info['genres'] = ", ".join(artist['genres']).title
        artist_info['id'] = artist['id']
        artist_info['popularity'] = artist['popularity']
        artist_info['link'] = artist['external_urls']['spotify']
        artists.append(artist_info)
    return artists