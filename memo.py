from datetime import datetime
import os.path as path
import sys
import urllib

import bleach
from flask import *

import database


def get_db():
    return database.get_db(g)

def init_db():
    database.init_db(g)


app = Flask(__name__)


with open(path.join(app.static_folder, "page_format.html"), 'r') as inp:
    PAGE_FORMAT = inp.read()


@app.teardown_appcontext
def close_connection(exception):
    db = get_db()
    db.close()


@app.route("/")
def index_page():
    filter_text = request.args.get('filter_text', None)
    cur = get_db().cursor()
    cur.execute("SELECT id, updated, item FROM memo ORDER BY updated DESC;")
    lines = []
    lines.extend(['<div class="px-3" id="items">', '<table class="table table-striped table-bordered">', '<tr><th>#</th><th>time</th><th>item</th></tr>'])
    for rid, rtime, rtext in cur.fetchall():
        if filter_text and filter_text not in rtext:
            continue  # for ri, rtime, rtext

        # drop subsecond digits
        i = rtime.find('.')
        if i >= 0:
            rtime = rtime[:i]

        lines.append("<tr><th>%s</th><td>%s</td><td>%s</td></tr>" % (rid, rtime, rtext))
    lines.extend(['</table>', '</div>'])
    return PAGE_FORMAT % '\n'.join(lines)


@app.route("/add", methods=['POST'])
def add_page():
    item_text = request.form['item']
    item_text = bleach.clean(item_text.strip())
    if item_text:
        cur = get_db().cursor()
        cur.execute("INSERT INTO memo (updated, item) values(?, ?);", [datetime.now(), item_text])
    return redirect('/')


@app.route("/filter", methods=['POST'])
def filter_page():
    filter_text = request.form['filter']
    if filter_text:
        return redirect('/?' + urllib.parse.urlencode({'filter_text': filter_text}))
    return redirect('/')


def main():
    argv = sys.argv[1:]
    if argv and argv[0] == 'init':
        with app.app_context():
            init_db()
        return
    app.run()


if __name__ == '__main__':
    main()
