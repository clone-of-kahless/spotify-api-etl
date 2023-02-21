import sqlalchemy
import pandas as pd
from sqlalchemy.orm import sessionmaker
import json
import requests
from datetime import datetime
import datetime
import sqlite3

DATABASE_LOCATION = "sqlite:///recently_played.sqlite"
USER_ID = "sheaftw"
TOKEN = "" # get token from https://developer.spotify.com/console/get-recently-played/

if __name__ == "__main__":

    #per Spotify API instructions
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {token}".format(token = TOKEN)
        }

    # Spotify's API takes datetime as UNIX ms
    # so, convert yesterday's date to that format
    # End goal is each day we want to load in yesterday's data/last 24 hours (:
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days = 1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 100

    request = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time = yesterday_unix_timestamp), headers = headers)

    data = request.json()

    #extract items of interest
    track_names = []
    artist_names = []
    played_at = []
    timestamps = []

    for track in data["items"]:
        track_names.append(track["track"]["name"])
        artist_names.append(track["track"]["album"]["artists"][0]["name"])
        played_at.append(track["played_at"])
        timestamps.append(track["played_at"][0:10])

    #prepare a dictionary for pd df
    
    track_dict = {
        "track_name" : track_names,
        "artist_name" : artist_names,
        "played_at" : played_at,
        "timestamp" : timestamps
        }

    track_df = pd.DataFrame(track_dict, columns = ["track_name", "artist_name", "played_at", "timestamp"])

    #print(track_df) # looks ok (: