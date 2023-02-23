import sqlalchemy
import pandas as pd
from sqlalchemy.orm import sessionmaker
import json
import requests
from datetime import datetime
import datetime
import time
import sqlite3

# OK -- the UNIX timestamp conversion though it corresponds to yesterday seems to be pulling back all kinds of irrelevant data (not within the boundaries set)
# I verified that the yesterday timestamp does correspond to yesterday.
# But Googling around, the timestamps do not act in a way consistent with how a lot of people expect for Spotify API 
# I'm not totally sure if that's my issue here or if there is some other bug I am missing. D: 
    # Anyway, I got what I needed out of this exercise -- get a baby pipeline connected to Airflow. 
    # I'll write up my notes for Airflow setup using WSL, maybe try to run it through Docker but this is fine for now then move onto original API pipeline project with more exhaustive validation.

# Defining ORM - Object Relational Mappers:
    # To retrieve data from the SQL database, you need to write some SQL obviously.
    # Python ORM allows you to query your data directly from Python without using SQL
    # ex. SQLAlchemy

#tutorial: https://github.com/karolina-sowinska/free-data-engineering-course-for-beginners/

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
    # yesterday = datetime.datetime.now() - datetime.timedelta(days = 1)
    # yesterday = yesterday.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    #     #ready for comparison to timestamp
    
    # timestamps = df["timestamp"].tolist()
    # for timestamp in timestamps:
    #     if datetime.datetime.strptime(timestamp, "%Y-%m-%d") != yesterday:
    #         raise Exception("At least one of the returned tracks not from yesterday.")

    return True

def run_spotify_etl():
    #Run within Windows:
    #database_location = r"C:\path\to\spotify-api-etl\recently_played_tracks.sqlite"
    #WSL/Airflow path:
    database_location = "/mnt/c/path/to/spotify-api-etl/recently_played_tracks.sqlite"
    #user_id = "sheaftw" #your user_id, not used? will probably be used for getting token
    api_token = "" 
    # get token from https://developer.spotify.com/console/get-recently-played/ (expires quickly, function to grab token needed if rerun)

    #per Spotify API instructions
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {token}".format(token = api_token)
        }

    # Spotify's API takes datetime as UNIX ms
    # so, convert yesterday's date to that format
    # End goal is each day we want to load in yesterday's data/last 24 hours
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days = 1)
    #yesterday_unix_timestamp = int(yesterday.timestamp()) * 100 # * 100 from tutorial not needed?
    yesterday_unix_timestamp = int(time.mktime(yesterday.timetuple()))
    #print('UNIX TIME STAMP, YESTERDAY:', yesterday_unix_timestamp)

    #https://developer.spotify.com/documentation/web-api/reference/#/operations/get-recently-played
    request = requests.get("https://api.spotify.com/v1/me/player/recently-played?limit=50&after={time}".format(time = yesterday_unix_timestamp), headers = headers)

    data = request.json()
    # print(data)
    
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

    # VALIDATE/TRANSFORM:
    if data_validation(track_df):
        print("Data validation checks passed. Proceed to load.")

    # LOAD:

    # create engine & pass in database location
        # database will be created if no db found @ DATABASE_LOCATION
    engine = sqlalchemy.create_engine('sqlite:///' + database_location)

    # connect to the database & create our cursor so we can point to specific rows in the db
    conn = sqlite3.connect(database_location)
    cursor = conn.cursor()

    # example of using SQL directly instead of ORM
        # tutorial uses default types of CHAR rather than datetime
    sql_table_creation_query = """
    CREATE TABLE IF NOT EXISTS my_played_tracks(
        track_name VARCHAR(200),
        artist_name VARCHAR(200),
        played_at VARCHAR(200),
        timestamp VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )
    """

    cursor.execute(sql_table_creation_query)
    print("Opened database successfully.")

    try:
        track_df.to_sql("my_played_tracks", engine, index = False, if_exists = "append")
    except:
        print("Data already exists in the database.")

    # close cursor:
    conn.close()
    print("Database closed.")

#run_spotify_etl()

# ? - What's a DAG?
    # DAG - Directed Acyclic Graph
    # Represents a series of events
    # Acyclic -> Does not cycle, you do not return to a previous event
    # Each DAG = a collection of tasks, organized in a way that reflects dependencies & relationships
    # Each node in a DAG is one task/function