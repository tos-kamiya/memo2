from datetime import datetime
import os.path as path
import os
import sqlite3

from flask import g


DATABASE = path.join(path.expanduser('~'), '.memo.py', 'database.db')


def get_db():
    database_dir = path.split(DATABASE)[0]
    if not path.isdir(database_dir):
        os.makedirs(database_dir)

    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, isolation_level=None)
    return db


def init_db():
    cur = get_db().cursor()
    cur.execute("DROP TABLE IF EXISTS memo;")
    cur.execute("CREATE TABLE memo(id INTEGER PRIMARY KEY, updated DATETIME, item TEXT);")
    cur.execute("INSERT INTO memo (updated, item) values(?, ?);", [datetime.now(), "--- database initialized ---"])
