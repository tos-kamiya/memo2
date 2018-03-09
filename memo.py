from datetime import datetime
import os.path as path
import re
import sys
import urllib

import bleach
from flask import *

from database import get_db, init_db


app = Flask(__name__)

with open(path.join(app.static_folder, "index_page.html"), 'r') as inp:
    INDEX_PAGE = inp.read()


@app.teardown_appcontext
def close_connection(exception):
    get_db(g).close()


@app.route("/")
def index_page():
    cur = get_db(g).cursor()
    cur.execute("SELECT id, updated, item FROM memo ORDER BY updated DESC;")
    records = cur.fetchall()

    filter_text = request.args.get('filter_text', None)
    if filter_text:
        records = [r for r in records if filter_text in r[2]]

    buf = []
    for rid, rt, item_text in records:
        rt = re.sub('[.][0-9]+$', '', rt)  # drop subsec digits
        buf.append("<tr><th>%s</th><td>%s</td><td>%s</td></tr>" % (rid, rt, item_text))
    html = INDEX_PAGE % '\n'.join(buf)

    return html


@app.route("/add", methods=['POST'])
def add_request():
    item_text = request.form['item']
    item_text = bleach.clean(item_text.strip())

    if item_text:
        sql = "INSERT INTO memo (updated, item) VALUES (?, ?);"
        get_db(g).cursor().execute(sql, [datetime.now(), item_text])

    return redirect('/')


@app.route("/filter", methods=['POST'])
def filter_request():
    filter_text = request.form['filter']

    if filter_text:
        param_str = '?' + urllib.parse.urlencode({'filter_text': filter_text})
        return redirect('/' + param_str)
    else:
        return redirect('/')


def main():
    argv = sys.argv[1:]
    if argv and argv[0] == 'init':
        with app.app_context():
            init_db(g)
        return

    app.run()


if __name__ == '__main__':
    main()
