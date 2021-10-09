### How to Run

- Run sql_commands.py to create the database
- Run download_data.py to continously download data and insert it to the database


    nohup python3 download_data.py &

- Run flask_app.py to analyze the data to find dips. The following code makes the app available on the local server via port 5000

```
    export FLASK_APP=flask_app.py
    flask run --host=0.0.0.0
```