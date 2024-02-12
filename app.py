import streamlit as st
import os
import base64
from requests import post, get
import json
import re  # For extracting the track ID from the input URL

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

# Function to get audio features
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

# Extract track ID from the Spotify link
def extract_track_id(spotify_link):
    match = re.search(r"open\.spotify\.com\/track\/([a-zA-Z0-9]+)", spotify_link)
    if match:
        return match.group(1)  # Returns the track ID
    else:
        st.error("Invalid Spotify link. Please make sure it's a valid track URL.")
        return None

# Streamlit UI
st.title("Spotify Song Audio Features Finder")

client_id = st.text_input("Client ID")
client_secret = st.text_input("Client Secret", type="password")

song_link = st.text_input("Enter Spotify song link")

if st.button("Get Audio Features"):
    if not client_id or not client_secret:
        st.error("Please enter your Client ID and Client Secret.")
    else:
        token = get_token(client_id, client_secret)
        if token:
            track_id = extract_track_id(song_link)
            if track_id:
                audio_features = get_audio_features(token, track_id)
                if audio_features:
                    st.json(audio_features)
                else:
                    st.error("Could not fetch audio features.")
            else:
                st.error("Please enter a valid Spotify song link.")
        else:
            st.error("Invalid credentials. Please check your Client ID and Client Secret.")
