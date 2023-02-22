from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from spotify_etl import run_spotify_etl

default_args = {
    'owner': 'airflow',
    'depends_on_past' : False,
    'start_date' : datetime(2023, 2, 20),
    'email_on_failure' : False,
    'email_on_retry' : False,
    'retries' : 1,
    'retry_delay' : timedelta(minutes = 1)
}

dag = DAG(
    'spotify_dag', #give it a name
    default_args = default_args,
    description = 'My first DAG <3 Spotify Recently Played',
    schedule_interval = timedelta(days = 1)
)

# Define operators -- what actually gets done by a task?
# One operator = 1 task in a DAG
# Here, we use a Python operator but there are several (bash, MySql, etc.)
# Operators don't share data with other operators
# You typically don't pass data between operators (if you really need to, you can use XCOM but not good practice)

run_etl = PythonOperator(
    task_id = 'whole_spotify_etl',
    python_callable = run_spotify_etl,
    dag = dag
)

run_etl
# we place the task we want to run at the bottom of the file
# if you have more tasks, you will use arrows here to specify the direction/represent the DAG
    # t1 >> [t2, t3]