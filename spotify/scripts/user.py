from typing import List, Dict
import statistics

def get_user_summary(sp) -> Dict:
    '''Returns users audio feature values

    Args:
        top_tracks: list of users top track objs

    Returns:
        dictionary of user summary info
            'artists': list of artist info; dict_keys(['followers', 'image', 
                'genres', 'link', 'popularity', 'name'])
            'genres': dict_keys(['top', 'other']) = (genre, percent)
                top: top 7 genres; other: rest of the genres
            'tracks': list of track info; dict_keys(['album_name', 'date', 'image',
                'artists', 'link', 'name', 'popularity'])
            'user': dict_keys(['email', 'image', 'name'])
            'user_features': dict_keys(['acousticness', 'danceability', 'energy',
                'instrumentalness', 'popularity', 'speechiness', 'tempo', 'valence'])
    '''
    summary_info = {}
    summary_info['id'], summary_info['name'], summary_info['email'], summary_info['image'] = get_user_profile_info(sp)
    summary_info['artists'], summary_info['genres'] = get_user_top_artist_info(sp)
    summary_info['tracks'], summary_info['user_features'] = get_user_top_track_info(sp)
    summary_info['artists'] = summary_info['artists'][0:20]
    summary_info['tracks'] = summary_info['tracks'][0:20]
    return summary_info

def get_user_profile_info(sp) -> Dict:
    user_info = {}
    user_profile = sp.me()
    false_link = 'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/271deea8-e28c-41a3-aaf5-2913f5f48be6/de7834s-6515bd40-8b2c-4dc6-a843-5ac1a95a8b55.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzI3MWRlZWE4LWUyOGMtNDFhMy1hYWY1LTI5MTNmNWY0OGJlNlwvZGU3ODM0cy02NTE1YmQ0MC04YjJjLTRkYzYtYTg0My01YWMxYTk1YThiNTUuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.BopkDn1ptIwbmcKHdAOlYHyAOOACXW0Zfgbs0-6BY-E'
    user_info['id'] = user_profile['id']
    user_info['name'] = user_profile['display_name']
    user_info['email'] = user_profile.get('email', "")
    user_info['image'] = user_profile['images'][-1] if user_profile['images'] else false_link
    return user_info['id'], user_info['name'], user_info['email'], user_info['image']

def get_user_top_artist_info(sp) -> Dict:
    artists = []
    genres = {}
    false_link = 'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/271deea8-e28c-41a3-aaf5-2913f5f48be6/de7834s-6515bd40-8b2c-4dc6-a843-5ac1a95a8b55.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzI3MWRlZWE4LWUyOGMtNDFhMy1hYWY1LTI5MTNmNWY0OGJlNlwvZGU3ODM0cy02NTE1YmQ0MC04YjJjLTRkYzYtYTg0My01YWMxYTk1YThiNTUuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.BopkDn1ptIwbmcKHdAOlYHyAOOACXW0Zfgbs0-6BY-E'
    genre_info = {'top': [], 'other': []}
    top_artists = sp.current_user_top_artists(time_range='long_term', limit=50)['items']
    genre_total = len(top_artists)
    for artist in top_artists:
        artist_info = {}
        artist_info['image'] = artist['images'][-1] if artist['images'] else false_link
        artist_info['name'] = artist['name']
        artist_info['followers'] = artist['followers']['total']
        artist_info['genres'] = ", ".join(artist['genres'])
        for genre in artist['genres']:
            genres[genre] = genres.get(genre, 0) + 1
        artist_info['popularity'] = artist['popularity']
        artist_info['link'] = artist['external_urls']['spotify']
        artists.append(artist_info)

    genres = sorted(genres.items(), key=lambda x: x[1], reverse = True)
    count = 0
    other_count = 0
    for k, v in genres:
        if count < 8:
            genre_info['top'].append((k.title(), v / genre_total * 100))
        else:
            genre_info['other'].append((k.title(), v / genre_total * 100))
            other_count += 1
        count += 1
    return artists, genre_info

def get_user_top_track_info(sp) -> Dict:
    tracks = []
    track_ids = []
    popularity = []
    user_features = {}
    top_tracks = sp.current_user_top_tracks(time_range='long_term', limit=50)['items']
    top_tracks = sp.tracks([track['id'] for track in top_tracks])['tracks']
    false_link = 'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/271deea8-e28c-41a3-aaf5-2913f5f48be6/de7834s-6515bd40-8b2c-4dc6-a843-5ac1a95a8b55.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzI3MWRlZWE4LWUyOGMtNDFhMy1hYWY1LTI5MTNmNWY0OGJlNlwvZGU3ODM0cy02NTE1YmQ0MC04YjJjLTRkYzYtYTg0My01YWMxYTk1YThiNTUuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.BopkDn1ptIwbmcKHdAOlYHyAOOACXW0Zfgbs0-6BY-E'
    for track in top_tracks:
        track_info = {}
        track_info['image'] = track['album']['images'][-1] if track['album']['images'] else false_link
        track_info['name'] = track['name']
        track_info['date'] = track['album']['release_date']
        track_info['album_name'] = track['album']['name']
        track_info['artists'] = ", ".join([artist['name'] for artist in track['artists']])
        track_info['popularity'] = track['popularity']
        track_info['preview'] = track['preview_url']
        popularity.append(track['popularity'])
        track_info['link'] = track['external_urls']['spotify']
        track_ids.append(track['id'])
        tracks.append(track_info)
    track_meta = get_audio_feature(sp, track_ids)
    track_meta['popularity'] = popularity
    for key in track_meta:
        stdev = statistics.stdev(track_meta[key])
        mean = statistics.mean(track_meta[key])
        if key != 'popularity':
            mean *= 100
        user_features[key] = (mean, stdev)
    return tracks, user_features

def get_audio_feature(sp, top_tracks: List[Dict]) -> Dict:
    '''Returns users audio feature values

    Args:
        top_tracks: list of users top track objs

    Returns:
        dictionary of values for each audio feature
    
    audio_feature keys: dict_keys(['danceability', 'energy', 'key', 'loudness', 
        'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 
        'valence', 'tempo', 'type', 'id', 'uri', 'track_href', 'analysis_url', 
        'duration_ms', 'time_signature'])
    '''
    track_meta = { 'danceability': [], 'energy': [], 'speechiness': [], 'tempo': [],
                    'valence': [], 'instrumentalness': [], 'acousticness': [], 'liveness': [] }
    audio_features = sp.audio_features(top_tracks)

    for track in audio_features:
        track_meta['danceability'].append(track['danceability'])
        track_meta['speechiness'].append(track['speechiness'])
        track_meta['energy'].append(track['energy'])
        track_meta['tempo'].append(track['tempo'])
        track_meta['valence'].append(track['valence'])
        track_meta['instrumentalness'].append(track['instrumentalness'])
        track_meta['acousticness'].append(track['acousticness'])
        track_meta['liveness'].append(track['liveness'])
    return track_meta

def get_user_playlists(sp):
    playlists_info = sp.current_user_playlists()['items']
    playlists = []
    for playlist in playlists_info:
        playlist_info = {}
        playlist_info['id'] = playlist['id']
        playlist_info['name'] = playlist['name']
        playlists.append(playlist_info)
    return playlists