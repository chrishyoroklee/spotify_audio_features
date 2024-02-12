import streamlit as st
import os
import base64
from requests import post, get
import json
import re  # For extracting IDs from the input URL

# Function to get the token
def get_token(client_id, client_secret):
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

# Function to get the authorization header
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

# Function to get audio features for a single track
def get_audio_features(token, track_id):
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    try:
        result.raise_for_status()
        json_result = result.json()
        return json_result
    except Exception as e:
        st.error(f"Error while fetching audio features: {e}")
        return None

# Extract track or playlist ID from the Spotify link
def extract_id(spotify_link, type="track"):
    if type == "track":
        match = re.search(r"open\.spotify\.com\/track\/([a-zA-Z0-9]+)", spotify_link)
    elif type == "playlist":
        match = re.search(r"open\.spotify\.com\/playlist\/([a-zA-Z0-9]+)", spotify_link)
    if match:
        return match.group(1)  # Returns the ID
    else:
        st.error(f"Invalid Spotify {type} link. Please make sure it's a valid URL.")
        return None

# Function to get playlist tracks
def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    all_tracks = []
    while url:
        response = get(url, headers=headers, params={"limit": 100})
        response.raise_for_status()  # This will stop the loop if an error occurs
        playlist_data = response.json()
        all_tracks.extend(playlist_data.get("items", []))
        url = playlist_data.get("next")  # Update the URL for the next request or None if at the end
    return all_tracks

# Function to get audio features for multiple tracks
def get_audio_features_for_tracks(token, track_ids):
    url = "https://api.spotify.com/v1/audio-features"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"ids": ",".join(track_ids)}
    try:
        response = get(url, headers=headers, params=params)
        response.raise_for_status()
        audio_features_data = response.json()
        return audio_features_data["audio_features"]
    except Exception as e:
        st.error(f"Error fetching audio features for tracks: {e}")
        return None

# Streamlit UI for Playlist
playlist_link = st.text_input("Enter Spotify playlist link")

if st.button("Get Playlist Audio Features"):
    if not client_id or not client_secret:
        st.error("Please enter your Client ID and Client Secret.")
    else:
        token = get_token(client_id, client_secret)
        if token:
            playlist_id = extract_id(playlist_link, type="playlist")
            if playlist_id:
                playlist_tracks = get_playlist_tracks(token, playlist_id)
                if playlist_tracks:
                    track_ids = [track['track']['id'] for track in playlist_tracks if track.get('track') and track['track'].get('id')]
                    if track_ids:
                        audio_features = get_audio_features_for_tracks(token, track_ids)
                        if audio_features:
                            for features in audio_features:
                                if features:  # Check if features were fetched successfully
                                    st.json(features)
                                else:
                                    st.write("Some audio features could not be fetched.")
                    else:
                        st.error("No valid track IDs found in the playlist.")
                else:
                    st.error("Failed to fetch playlist tracks.")
            else:
                st.error("Please enter a valid Spotify playlist link.")
        else:
            st.error("Invalid credentials. Please check your Client ID and Client Secret.")

# Existing UI for single song
if st.button("Get Track Audio Features"):
    if not client_id or not client_secret:
        st.error
