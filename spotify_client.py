import requests
import os
import json
#import spotipy
#from spotipy.oauth2 import SpotifyOAuth
import base64
from random import randint

CLIENT_ID=os.environ["CLIENT_ID"]
CLIENT_SECRET=os.environ["CLIENT_SECRET"]
USER_ID=os.environ["USER_ID"]
REFRESH_TOKEN=os.environ["REFRESH_TOKEN"]

class Spotify_Client():
    def __init__(self):
        self.rf_token = REFRESH_TOKEN
        self.refresh_token()
        
    def refresh_token(self):
        client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        token_headers = {
            'Authorization': f"Basic {client_creds_b64.decode()}"
        }
        url = f"https://accounts.spotify.com/api/token"
        form_data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.rf_token,
        }
        
        server = requests.post(url, headers=token_headers, data=form_data)
        output = server.json()
        self.access_token = output['access_token']

    def get_playlists(self, name):
        '''
        Search for a list with given name, it found returns id if not False
        '''
        url = f"https://api.spotify.com/v1/users/{USER_ID}/playlists"
        server = requests.get(url, headers={'Authorization': f'Bearer {self.access_token}','Accept': 'application/json'})

        for playlist in server.json()["items"]:
            if playlist["name"] == name:
                self.snapshot = playlist["snapshot_id"]
                return playlist["id"] 
        return False
    
    def find_duplicated_tracks(self,tracks):
        '''
        Find duplicated tracks on a playlist and removes then (the duplicates)
        '''
        unique = []
        dupes = []
        for track in tracks:
            if track in unique:
                dupes.append(track)
            else:
                unique.append(track)

        print(tracks)
        #dupes = [x for n, x in enumerate(tracks) if x in tracks[:n]]

        return(dupes)
                
    def delete_duplicate(self,playlist,uri):
        url = f"https://api.spotify.com/v1/playlists/{playlist}/tracks"
        
        form_data = {
            "tracks": [{"uri": uri}],
            "snapshot_id": self.snapshot,
        }
        server = requests.delete(url, headers={'Authorization': f'Bearer {self.access_token}','Accept': 'application/json'}, data=json.dumps(form_data))
        print(f'Deleting {uri} and adding again')
        #print(server.__dict__)
        # Add again
        self.add_to_playlist(playlist,uri)

    def add_to_playlist(self,playlist,uri):
        url = f"https://api.spotify.com/v1/playlists/{playlist}/tracks?uris={uri}"
        form_data = {
            "uris": [ uri ],
        }
        server = requests.post(url, headers={'Authorization': f'Bearer {self.access_token}','Content-Type': 'application/json'}, data=form_data)

    def reorder(self, track, pos, max, playlist):
        value = randint(0, max)
        url = f"https://api.spotify.com/v1/playlists/{playlist}/tracks"
        form_data = {
            "range_start": pos,
            "insert_before": value,
            "snapshot_id": self.snapshot,
        }
        print(f'Reordering {track} from {pos} to {value}')
        server = requests.put(url, headers={'Authorization': f'Bearer {self.access_token}','Content-Type': 'application/json'}, data=json.dumps(form_data))
    
    def get_playlist_tracks(self,playlist_id):
        tracks = []
        offset = 0
        while len(tracks)==offset:
            url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=50&offset={offset}"
            server = requests.get(url, headers={'Authorization': f'Bearer {self.access_token}','Accept': 'application/json'})

            for track in server.json()["items"]:
                track_dict = {
                    "id": track["track"]["id"],
                    "artist": track["track"]["artists"][0]["name"],
                    "title": track["track"]["name"],
                    "uri": track["track"]['uri']
                }
                tracks.append(track_dict)
            offset += 50
        # Reorder playlist
        value = randint(0, len(tracks))
        self.reorder(track=tracks[value],pos=value, max=len(tracks),playlist=playlist_id)

        # Remove dupes
        dupes = self.find_duplicated_tracks(tracks)
        for dupe in dupes:
            print(dupe)
            self.delete_duplicate(playlist=playlist_id, uri=dupe['uri'], )
            break




def main():
    spotify_client = Spotify_Client()

    playlist_names = ["Mis favoritos", "Mi Indie"]

    for playlist_name in playlist_names:
        playlist = spotify_client.get_playlists(playlist_name)
        if playlist:
            spotify_client.get_playlist_tracks(playlist)



if __name__ == '__main__':
    '''
    scope = "user-library-read,playlist-modify-private,,playlist-modify-public"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])
    '''
    main()
