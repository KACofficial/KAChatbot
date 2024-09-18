import os
import requests
from flask import (
    Flask,
    request,
    redirect,
    session,
    url_for,
    render_template,
    jsonify,
    Response,
)
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from utils.config_utils import *  # load_spotify_config, load_twitch_config, load_config, push_config
from  utils import time_utils
import logging
import random
from utils.chatlog_utils import Chatlog

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app)

spotify_config = load_spotify_config()
SPOTIPY_CLIENT_ID = spotify_config["client_id"]
SPOTIPY_CLIENT_SECRET = spotify_config["client_secret"]
SPOTIPY_REDIRECT_URI = spotify_config["redirect_url"]

SCOPE = "user-read-playback-state"

sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE,
)

twitch_config = load_twitch_config()
TWITCH_CLIENT_ID = twitch_config["client_id"]
TWITCH_CLIENT_SECRET = twitch_config["client_secret"]
TWITCH_REDIRECT_URI = twitch_config["redirect_url"]
TWITCH_SCOPE = twitch_config["scopes"]

TWITCH_AUTH_URL = "https://id.twitch.tv/oauth2/authorize"
TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"

global_config = load_config()

fishbowl = {"fishlist": []}
lurkers = []
chatlog = Chatlog()

@app.route("/")
def index():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route("/callback")
def callback():
    # Retrieve the access token from Spotify
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)

    # Store token info in session
    session["token_info"] = token_info
    return redirect(url_for("currently_playing"))


@app.route("/currently_playing")
def currently_playing():
    # Check token expiration and refresh if necessary
    token_info = session.get("token_info", {})

    if not token_info:
        return redirect(url_for("index"))  # Reauthenticate if no token info exists

    # Check if token has expired
    if sp_oauth.is_token_expired(token_info):
        # Ensure we have a refresh_token before trying to refresh
        if "refresh_token" in token_info:
            token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
            session["token_info"] = token_info
        else:
            return redirect(url_for("index"))  # If no refresh_token, redirect to login
    sp = spotipy.Spotify(auth=token_info["access_token"])

    # Get the currently playing track
    current_track = sp.current_playback()

    if current_track and current_track["is_playing"]:
        song = current_track["item"]["name"]
        artists = ", ".join(
            [artist["name"] for artist in current_track["item"]["artists"]]
        )
        album_cover = current_track["item"]["album"]["images"][0][
            "url"
        ]  # Get the album cover image (usually the largest one)
        return render_template(
            "currently_playing.html",
            song=song,
            artists=artists,
            album_cover=album_cover,
        )
        # return {'song': song, 'artists': artists, 'album_cover': album_cover}
    else:
        return render_template("not_playing.html")


@app.route("/currently_playing_json")
def currently_playing_json():
    # Check token expiration and refresh if necessary
    token_info = session.get("token_info", {})

    if not token_info:
        return redirect(url_for("index"))  # Reauthenticate if no token info exists

    # Check if token has expired
    if sp_oauth.is_token_expired(token_info):
        # Ensure we have a refresh_token before trying to refresh
        if "refresh_token" in token_info:
            token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
            session["token_info"] = token_info
        else:
            return redirect(url_for("index"))  # If no refresh_token, redirect to login
    sp = spotipy.Spotify(auth=token_info["access_token"])

    # Get the currently playing track
    current_track = sp.current_playback()

    if current_track and current_track["is_playing"]:
        song = current_track["item"]["name"]
        artists = ", ".join(
            [artist["name"] for artist in current_track["item"]["artists"]]
        )
        album_cover = current_track["item"]["album"]["images"][0][
            "url"
        ]  # Get the album cover image (usually the largest one)
        return jsonify({"title": song, "artists": artists}), 200
        # return {'song': song, 'artists': artists, 'album_cover': album_cover}
    else:
        return jsonify({"title": None, "artists": None}), 204


@app.route("/twitch_login")
def twitch_login():
    twitch_auth_url = f"{TWITCH_AUTH_URL}?response_type=code&client_id={TWITCH_CLIENT_ID}&redirect_uri={TWITCH_REDIRECT_URI}&scope={TWITCH_SCOPE}"
    return redirect(twitch_auth_url)


@app.route("/twitch_callback")
def twitch_callback():
    code = request.args.get("code")

    token_data = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": TWITCH_REDIRECT_URI,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # Exchange the authorization code for an access token
    response = requests.post(TWITCH_TOKEN_URL, data=token_data, headers=headers)
    token_data = response.json()

    if "access_token" in token_data:
        session["twitch_access_token"] = token_data["access_token"]
        refresh_token = token_data.get("refresh_token")

        # Update the configuration
        twitch_config["access_token"] = token_data["access_token"]
        if refresh_token:
            twitch_config["refresh_token"] = refresh_token

        global_config["twitch"] = twitch_config
        push_config(global_config)

        return "Twitch Access Token obtained and saved!"
    else:
        return Response(
            f"Error obtaining Twitch token: {token_data}", mimetype="text/plain"
        )


@app.route("/fishbowl")
def fishbowl_page():
    return render_template("fishbowl.html", fishlist=fishbowl["fishlist"])


@app.route("/add-fish/<name>/<fishtype>", methods=["POST"])
def add_fish(name, fishtype):
    if name and fishtype:
        # Check if the name already exists in the fishlist
        if any(fish["name"] == name for fish in fishbowl["fishlist"]):
            return jsonify({"status": "error", "message": "Fish already exists"}), 400

        # If the name doesn't exist, add it to the fishlist with random initial positions
        fishbowl["fishlist"].append(
            {
                "name": name,
                "image": "fish",
                "color": None,
                "position": {"x": random.randint(0, 1280), "y": random.randint(0, 720)},
            }
        )

        if fishtype.lower() == "vip":
            fishbowl["fishlist"][-1]["color"] = "#f1c40f"
        elif fishtype.lower() == "broadcaster":
            fishbowl["fishlist"][-1]["color"] = "#c0392b"
        elif fishtype.lower() == "mod":
            fishbowl["fishlist"][-1]["color"] = "#1bbf4f"
        else:
            fishbowl["fishlist"][-1]["color"] = "whitesmoke"

        socketio.emit("update_fishbowl", fishbowl["fishlist"])
        return jsonify({"status": "success", "message": "Fish added successfully"}), 200

    return jsonify({"status": "error", "message": "Invalid name"}), 400


@app.route("/remove-fish/<name>", methods=["POST"])
def remove_fish(name):
    if name:
        # Check if the name exists in the fishlist
        fish = next(
            (fish for fish in fishbowl["fishlist"] if fish["name"] == name), None
        )
        if fish:
            fishbowl["fishlist"].remove(fish)
            socketio.emit("update_fishbowl", fishbowl["fishlist"])
            return (
                jsonify({"status": "success", "message": "Fish removed successfully"}),
                200,
            )

        return jsonify({"status": "error", "message": "Fish not found"}), 400


@app.route("/clear-fishbowl", methods=["POST"])
def clear_fishbowl():
    fishbowl["fishlist"] = []
    socketio.emit("update_fishbowl", fishbowl["fishlist"])
    return (
        jsonify({"status": "success", "message": "Fishbowl cleared successfully"}),
        200,
    )


@app.route("/lurk/<username>", methods=["POST"])
def lurk(username):
    if username in lurkers:
        return (
            jsonify({"status": "error", "message": "Lurker already exists"}),
            400,
        )
    lurkers.append(username)
    socketio.emit("add_lurker", username)
    return (
        jsonify({"status": "success", "message": "Lurker added successfully"}),
        200,
    )

@app.route("/unlurk/<username>", methods=["POST"])
def unlurk(username):
    try:
        lurkers.remove(username)
        socketio.emit("remove_lurker", username)
        return (
            jsonify({"status": "success", "message": "Lurker removed successfully"}),
            200,
        )
    except ValueError:
        return (
            jsonify({"status": "error", "message": "Lurker not found"}),
            400,
        )

@app.route("/dashboard", defaults={'page': None})
@app.route("/dashboard/<page>")
def dashboard(page):
    if page == "chatlog":
        channel = request.args.get("channel", default='all', type=str)
        date = request.args.get("date", default=time_utils.get_current_time("%m-%d-%Y"), type=str)
        print(f"Requested channel: {channel}, date: {date}")

        if channel == 'all':
            chatlog_data = chatlog.read_chatlog(date=date)
        else:
            chatlog_data = chatlog.read_chatlog(channel=channel, date=date)
        
        # socketio.emit("update_chatlog", chatlog_data)
        
        return render_template("dashboard-chatlog.html", chatlog=chatlog_data)
    else:
        return render_template("dashboard-main.html", lurkers=lurkers)




@socketio.on("connect")
def handle_connect():
    emit("update_fishbowl", fishbowl["fishlist"])

@socketio.on("request_chatlog")
def handle_request_chatlog(data):
    channel = data.get("channel", 'all')
    date = data.get("date", time_utils.get_current_time("%m-%d-%Y"))
    if date == "":
        date = time_utils.get_current_time("%m-%d-%Y")

    if channel == 'all':
        chatlog_data = chatlog.read_chatlog(date=date)
    else:
        chatlog_data = chatlog.read_chatlog(channel=channel, date=date)

    # print(f"Emitting chatlog data: {chatlog_data}")
    emit("update_chatlog", chatlog_data)

def run_webui():
    app.run(debug=False, use_reloader=False)


if __name__ == "__main__":
    run_webui()
