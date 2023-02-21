import sqlalchemy
import pandas as pd
from sqlalchemy.orm import sessionmaker
import json
import requests
from datetime import datetime
import datetime
import sqlite3

#tutorial: https://github.com/karolina-sowinska/free-data-engineering-course-for-beginners/

DATABASE_LOCATION = "sqlite:///recently_played.sqlite"
USER_ID = "sheaftw" #your user_id
TOKEN = "" 
    # get token from https://developer.spotify.com/console/get-recently-played/

def data_validation(df: pd.DataFrame) -> bool:

    # Check if empty 
    if df.empty:
        print("No data found. Finishing execution.")
        return False
    
    # primary key: played_at
    # Primary Key Check - Raise Exception if duplicates
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary key violated.")

    # check for null values:
    if df.isnull().values.any():
        raise Exception("Null values found.")

    # check data only includes that listened to/timestamps within past 24 hours
    yesterday = datetime.datetime.now() - datetime.timedelta(days = 1)
    yesterday = yesterday.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
        #ready for comparison to timestamp
    
    timestamps = df["timestamp"].tolist()
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, "%Y-%m-%d") != yesterday:
            raise Exception("At least one of the returned tracks not from yesterday.")

    return True

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
    #print(data)
    
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

    if data_validation(track_df):
        print("Data validation checks passed. Proceed to load.")