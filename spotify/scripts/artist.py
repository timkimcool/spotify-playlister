from typing import Dict, List
def get_artist_info(sp, artist_id):
    '''Get artist info

    Args:
        artist_id = spotify artist id

    Returns:
        artist dict:
            ['artist'] = dict of current artist popularity, genre, name, id, link, image, followers
            ['tracks'] = list of top tracks with date, name, image, album, album_link, artist, track_link, name, popularity
            ['albums'] = list of 50 most recent albums with date, image, group, album_link, artists
            ['related_artists'] = list of related artists with popularity, genres, name, id, link, image, # followers 
    '''
    artist_info = {}

    artist = {}
    artist_results = sp.artist(artist_id)
    artist['popularity'] = artist_results['popularity']
    artist['genres'] = artist_results['genres']
    artist['name'] = artist_results['name']
    artist['id'] = artist_results['id']
    artist['link'] = artist_results['external_urls']['spotify']
    artist['image'] = artist_results['images'][1]
    artist['followers'] = artist_results['followers']['total']
    artist_info['artist'] = artist

    top_track_results = sp.artist_top_tracks(artist_id)['tracks']
    tracks = []
    for track in top_track_results:
        track_info = {}
        track_info['date'] = track['album']['release_date']
        track_info['image'] = track['album']['images'][1]
        track_info['album'] = track['album']['name']
        track_info['album_link'] = track['album']['external_urls']['spotify']
        track_info['artists'] = [artist['name'] for artist in track['artists']]
        track_info['track_link'] = track['external_urls']['spotify']
        track_info['name'] = track['name']
        track_info['popularity'] = track['popularity']
        tracks.append(track_info)
        # @TODO: audio features?
    artist_info['tracks'] = tracks

    albums = []
    album_results = sp.artist_albums(artist_id, limit=50)['items']
    for album in album_results:
        album_info = {}
        album_info['date'] = album['release_date']
        album_info['name'] = album['name']
        album_info['image'] = album['images'][1] if album['images'] else 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'
        album_info['group'] = album['album_group']
        album_info['album_link'] = album['external_urls']['spotify']
        album_info['artists'] = [artist['name'] for artist in album['artists']]
        albums.append(album_info)
    artist_info['albums'] = albums

    related_artists = []
    related_artist_results = sp.artist_related_artists(artist_id)['artists']
    for artist in related_artist_results:
        related_artist_info = {}
        related_artist_info['popularity'] = artist['popularity']
        related_artist_info['genres'] = artist['genres'].title()
        related_artist_info['name'] = artist['name']
        related_artist_info['id'] = artist['id']
        related_artist_info['link'] = artist['external_urls']['spotify']
        related_artist_info['image'] = artist['images'][1]
        related_artist_info['followers'] = artist['followers']['total']
        related_artists.append(related_artist_info)
    artist_info['related_artists'] = related_artists
    
    return artist_info

def get_artist_tracks(sp, artist_id: str) -> List[tuple]:
    '''Returns all songs by artist

    Args:
        artist_id: id of artist

    Returns:
        dict of [track_id] = 'name': name, 'date': date, 'popularity': popularity
    '''
    track_dict = {}
    artists_top_tracks = sp.artist_top_tracks(artist_id)['tracks']
    top_tracks = { k['id']: True for k in artists_top_tracks }
    artist_albums = sp.artist_albums(artist_id, limit=40)['items']
    album_ids = [album['id'] for album in artist_albums]
    if len(album_ids) > 20:
        albums = sp.albums(album_ids[0:20])['albums'] + sp.albums(album_ids[20:])['albums']
    else:
        albums = sp.albums(album_ids)['albums']
    for album in albums:
        tracks = album['tracks']['items']
        for track in tracks:
            for artist in track['artists']:
                if artist['id'] == artist_id:
                    track_dict[track['id']] = {
                        'name': track['name'],
                        'date': album['release_date'],
                    }
    key_lst = list(track_dict.keys())
    for i in range(len(key_lst) // 50 + 1):
        keys = key_lst[i * 50:i * 50 + 50]
        tracks = sp.tracks(keys)['tracks']
        for track in tracks:
            track_dict[track['id']]['popularity'] = track['popularity']
            track_dict[track['id']]['link'] = track['external_urls']['spotify']
            track_dict[track['id']]['image'] = track['album']['images'][-1] if track['album']['images'] else False
            track_dict[track['id']]['preview'] = track['preview_url']
            track_dict[track['id']]['album_name'] = track['album']['name']
            track_dict[track['id']]['artists'] = ", ".join([artist['name'] for artist in track['artists']])
            track_dict[track['id']]['id'] = track['id']
            if track['id'] in top_tracks:
                track_dict[track['id']]['top'] = True
    tracks = []
    for _, v in track_dict.items():
        tracks.append(v)
    
    artists1 = sp.artist_related_artists(artist_id)['artists']
    artists = []
    for artist in artists1:
        artist_info = {}
        artist_info['link'] = artist['external_urls']['spotify']
        artist_info['image'] = artist['images'][-1] if artist['images'] else False
        artist_info['id'] = artist['id']
        artist_info['name'] = artist['name']
        artist_info['popularity'] = artist['popularity']
        artists.append(artist_info)
    return { 'tracks': sorted(tracks, reverse=True, key=lambda x: x['date']), 'artists': artists }

def get_similar_tracks_track(sp, track_id, user_features):
    recommended_tracks = sp.recommendations(seed_tracks=[track_id], limit=50,
        target_danceability=user_features['danceability'][0],
        target_energy=user_features['energy'][0],
        target_speechiness=user_features['speechiness'][0],
        target_valence=user_features['valence'][0],
        target_tempo=user_features['tempo'][0])['tracks']
    
    tracks = []
    for track in recommended_tracks:
        track_dict = {}
        track_dict['popularity'] = track['popularity']
        track_dict['link'] = track['external_urls']['spotify']
        track_dict['image'] = track['album']['images'][-1] if track['album']['images'] else False
        track_dict['preview'] = track['preview_url']
        track_dict['album_name'] = track['album']['name']
        track_dict['artists'] = ", ".join([artist['name'] for artist in track['artists']])
        track_dict['id'] = track['id']
        track_dict['name'] = track['name']
        tracks.append(track_dict)
    return { 'tracks': sorted(tracks, reverse=True, key=lambda x: x['popularity']) }

def get_similar_tracks_artist(sp, artist_id, user_features):
    recommended_tracks = sp.recommendations(seed_artists=[artist_id], limit=50,
        target_danceability=user_features['danceability'][0],
        target_energy=user_features['energy'][0],
        target_speechiness=user_features['speechiness'][0],
        target_valence=user_features['valence'][0],
        target_tempo=user_features['tempo'][0])['tracks']
    
    tracks = []
    for track in recommended_tracks:
        track_dict = {}
        track_dict['popularity'] = track['popularity']
        track_dict['link'] = track['external_urls']['spotify']
        track_dict['image'] = track['album']['images'][-1] if track['album']['images'] else False
        track_dict['preview'] = track['preview_url']
        track_dict['album_name'] = track['album']['name']
        track_dict['artists'] = ", ".join([artist['name'] for artist in track['artists']])
        track_dict['id'] = track['id']
        track_dict['name'] = track['name']
        tracks.append(track_dict)
    return { 'tracks': sorted(tracks, reverse=True, key=lambda x: x['popularity']) }
