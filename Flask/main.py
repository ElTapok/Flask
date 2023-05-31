import random
from datetime import datetime
import pytz
import os
import psycopg2
import psycopg2.extras
from flask.cli import with_appcontext
import click

from flask import Flask, request, render_template, g, current_app


app = Flask(__name__)

### Routes


@app.route("/dump")
def dump_entries():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('select id, date, title, content from entries order by date')
    rows = cursor.fetchall()
    output = ""
    for r in rows:
        debug(str(dict(r)))
        output += str(dict(r))
        output += "\n"
    return "<pre>" + output + "</pre>"

@app.route("/browse")
def browse():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('select id, date, title, content from entries order by date')
    rowlist = cursor.fetchall()
    return render_template('browse.html', entries=rowlist)

def connect_db():
    """Connects to the database."""
    debug("Connecting to DB.")
    conn = psycopg2.connect(host="localhost", user="postgres", password="123", dbname="FlaskApp", 
        cursor_factory=psycopg2.extras.DictCursor)
    return conn
    
def get_db():
    """Retrieve the database connection or initialize it. The connection
    is unique for each request and will be reused if this is called again.
    """
    if "db" not in g:
        g.db = connect_db()

    return g.db
    
@app.teardown_appcontext
def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()
        debug("Closing DB")

@app.cli.command("initdb")
def init_db():
    """Clear existing data and create new tables."""
    conn = get_db()
    cur = conn.cursor()
    with current_app.open_resource("schema.sql") as file: 
        alltext = file.read() 
        cur.execute(alltext) 
    conn.commit()
    print("Initialized the database.")

@app.cli.command('populate')
def populate_db():
    conn = get_db()
    cur = conn.cursor()
    with current_app.open_resource("populate.sql") as file: 
        alltext = file.read() 
        cur.execute(alltext) 
    conn.commit()
    print("Populated DB with sample data.")

@app.route("/random")
def pick_word():
    random_word_list = ['Олександр', 'Федоренко', 'КІД-22']
    random_word = random.choice(random_word_list)
    print(random_word)
    return render_template("random.html", word=random_word)

@app.route("/time")
def get_time():
    now = datetime.now().astimezone(pytz.timezone("US/Central"))
    timestring = now.strftime("%Y-%m-%d %H:%M:%S")  
    beginning = "<html><body><h1>The time is: "
    ending = "</h1></body></html>"
    return render_template("time.html", timestring=timestring)
  
@app.route("/")
def hello_world():
    return "Hello, world!"  

def debug(s):
    """Prints a message to the screen (not web browser) 
    if FLASK_DEBUG is set."""
    if app.config['DEBUG']:
        print(s)
      
### Start flask
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9090, debug=True)