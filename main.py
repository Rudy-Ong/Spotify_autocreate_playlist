import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from pprint import pprint
import os
from dotenv import load_dotenv

load_dotenv()

# From Billboard Top 100 Music Website scrape 100 titles top music at given date
date = input("Which date do you want to travel to? (format YYYY-MM-DD):")
year = date.split("-")[0]
month = date.split("-")[1]
billboard_endpoint = f"https://www.billboard.com/charts/hot-100/{date}"

response = requests.get(url=billboard_endpoint)
billboard_top100 = response.text

soup = BeautifulSoup(billboard_top100, "html.parser")
music_title_elements = soup.select(selector="li > #title-of-a-story")
music_title_list = [title.getText(strip=True) for title in music_title_elements]

# From Spotify use Spotipy API to authorize with your account, create a playlist and insert music track
spotipy_redirecturi= "https://example.com"

spotify_user_name = os.environ.get("YOUR_USER_ID")
spotify_client_id = os.environ.get("YOUR_CLIENT_ID")
spotify_client_secret = os.environ.get("YOUR_CLIENT_SECRET")

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="https://example.com",
        client_id=spotify_client_id,
        client_secret=spotify_client_secret,
        show_dialog=True,
        cache_path="token.txt",
        username=spotify_user_name, 
    )
)

user_id = sp.current_user()["id"]

song_uri_list = []
for song in music_title_list:
    result = sp.search(q=f"track:{song}, year:{year}", type="track")
    try:   
        uri = result["tracks"]["items"][0]["uri"]
        song_uri_list.append(uri)
    except IndexError:
        print(f"{song} song not found in Spotify. Skipped.")


# Create a Playlist
playlist_name = f"{date} Billboard Hot 100"
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)

# Insert song by URI (for free tier, in one request, 100 or less track songs could be insert)
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uri_list)