### General notes for future me:

I used Karolina Sowinska's [very simple ETL Airflow tutorial](https://github.com/karolina-sowinska/free-data-engineering-course-for-beginners/) to try Airflow out for the first time and have basically copied her code here. She builds a very simple pipeline in Python from Spotify's API to feed into a SQLite database. [Here](https://youtu.be/dvviIUKwH7o) is the first video in the series on YouTube.

It looks like Karolina uses Mac so it was a little squirrelly getting my pipeline running on Windows. Generally, it seems the advice for using Airflow if you have a Windows machine is to use WSL or Docker to get Airflow running on Windows as it relies heavily on bash scripting. I used WSL and will run through Docker another time.

As an aside, Spotify API seems to have some issues with timestamps not working as expected? This may be my misunderstanding but I got what I needed out of this exercise so I'll be moving forward and resisting my impulse to dig deeper and deeper into this until I find out for sure.

Here are my notes for future Shea on how I got Airflow running on Windows for this tutorial, running Airflow using WSL but pointing to a dags folder in my Windows environemnt:

### Notes for getting Airflow running on Windows:

Getting Airflow running on Windows was a whole thing. Deep breaths. Don't get all frustrated, man.

Here are my notes on what I did this time, in case/when I need to do it again --

If someone else is reading this, bear in mind that *I'm new to Airflow and bash* so this may not be the best way to do it but it did what I wanted it to do.

1. Install WSL (Ubuntu) and Windows Terminal, if not already installed.
To install WSL, you can follow [these steps from Microsoft](https://learn.microsoft.com/en-us/windows/wsl/install).

If you don't already have Windows terminal on your machine, it is *so good*. **SO GOOD** I may stop putting off my Windows 11 upgrade because they let you set it as the default terminal.

Anyway, I installed the Ubuntu WSL.

2. Open up an Ubuntu window in Windows Terminal. 

If you want to see your active directory within Windows Explorer at any time, you can use the command: `explorer.exe .`

3. Linux should come with Python 3. You then want to add these packages so you can use pip.

`sudo apt-get install software-properties-common`
`sudo apt-add-repository universe`
`sudo apt-get update`

4. Check your Python version. Airflow at the time of writing this does not support 3.11 so you may need to swap your version to 3.10 or prior.

Then, use venv to set up a virtual environment within your Linux home directory.
`python3 -m venv /airflow-venv`

You can us the `ls` command to see your airflow-venv folder hanging out in there but stay hanging out in home, ~, for now.

5. Activate the environment: `source airflow-venv/bin/activate`

Make sure you have all the Python packages you'll need to run your dags installed in this environment, like pandas and such. :)

6. I then used Airflow's Quick Start guide with some modifications:
    - Make a directory for airflow: `mkdir airflow`
    You can use ls to make sure it's there.
    - Set AIRFLOW_HOME variable value: `export AIRFLOW_HOME=~/airflow`
    - Now, anytime you want, you can use `cd $AIRFLOW_HOME` within the Ubuntu terminal to get to your airflow directory.

6. Install the apache-airflow package with pip according to Quick Start instructions.
Ex., If you're using Python 3.10 and installing v 2.5.1:
`pip install "apache-airflow==2.5.1" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.5.1/constraints-3.10.txt"`

7. To initialize airflow so you can see your config file, you may be able to just use `airflow` but I used the command: `airflow db init `

8. Changing your directory to the airflow directory (`cd ~/airflow` or `cd #AIRFLOW_HOME`), you can use `ls` to see your files there. 

If you want to see these files in Windows explorer, from ~/airflow, enter `explorer.exe .` to open your current directory in Windows Explorer.

9. There should be airflow.cfg file in there. Open it up in your text editor of choice. Some people use nano for this but I'm not so cool yet.

10. In the config file, airflow.cfg, change the dags_folder configuration to point to the folder where your "dags"/automation scripts will be. It is one of the first lines in the config file.

To point to a location on your Windows file system, you'll need to do it like you would to cd to a Windows file system in the terminal. 

Like so:  
dags_folder = /mnt/c/users/username/path/to/dags

Additionally, change the load_examples configuation to False unless you want all the pre-gen dags to start up when you start up the webserver.

Like so:  
load_examples = False

*Note:* If you have relative paths in your Python script (say for creating/accessing a local SQLite database as in many tutorials) that point to Windows subdirectories, you can do stuff there by ensuring you provide the full path as if you were trying to access those directories from your WSL. You can use a path library for this in practice obviously but just as an quick & dirty example, the path string you're inputting will be formatted such that "C:\\" is replaced with "/mnt/c/". E.g.,

`database_location = "/mnt/c/users/username/path/to/dir/sqlite_db.sqlite"`

11. Create a user before spinning up the scheduler and webserver. I think this is optional but it seems to be good practice and it is what I did when I got things to work how I wanted them to.

Users are created using the command:
`airflow users create`
So, you can get some good guidance if you input
`airflow users create --help` 
or, equivalently:
`airflow users create -h`

Just in general, `airflow --help` was really helpful to me in having some semblance of an idea of what I was doing. Don't sleep on that!

12. Anyway, once you've made your little admin account, you'll want to open TWO additional Ubuntu windows/tabs.

Don't forget to activate your venv or you'll probably get package import errors.

In one tab, spin up the scheduler: 
`airflow scheduler`
In the other, spin up the webserver. You can also explicitly specify the port here with 8080 being the default, I think.
`airflow webserver -p 8080`

13. Use your browser to navigate to localhost:8080, log in with your admin account credentials you made earlier and voila! You should see your dag there. In the case of this project, it's called "spotify_dag" and from there, you can play around and view log files and such.

Now, you should see your DAGs in there IF the file name has "dag" somewhere in it. This is somewhere in the config file if you want to load all the .py files, regardless of if they're dags but that doesn't strike me as optimal.

**Other things:**

*Aside 1: You can tear down the airflow database and reset it which can be nice when things are wonky.*
`airflow db reset`
`airflow db init`

*Aside 2: Where are my dags?*
There seem to be lots of ways your dags might not show up but for me, these are the issues I had:

1. If you run:
`airflow dags list`
and no files appear, you may have set dags_folder in your config file incorrectly. 

Try using cd in the terminal with the path as it appears there and see if that's really the path you're trying to point to.

If you get an error indicating that the files failed to load and prompting you to check the import errors, ... check the import errors, my dude.

2. If you run:
`airflow dags list-import-errors`
You'll see if your Python code raised an exception anywhere. 

It looks like it'll actually run your code to return the execution errors to you so, you know, be wary of that.

### fin
OK - That should be enough notes for you, future Shea. (I hope!)

Thanks to these resources from my Googling frenzy (and others, I'm sure, now lost to time):
https://airflow.apache.org/docs/apache-airflow/stable/start.html
https://learn.microsoft.com/en-us/windows/wsl/install
https://stackoverflow.com/questions/32378494/how-to-run-airflow-on-windows which references
https://coding-stream-of-consciousness.com/2018/11/06/apache-airflow-windows-10-install-ubuntu/
(This one also references a link to the same blog installing Airflow via Docker. Shout out to John Humphreys!)