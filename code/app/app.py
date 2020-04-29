import os
import pickle
import threading

from flask import Flask, render_template

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def get_symbols():
    if os.path.exists(os.path.join(DATA_DIR, "symbols.pkl")):
        with open(os.path.join(DATA_DIR, "symbols.pkl"), "rb") as f:
            symbols = pickle.load(f)
    return symbols


def get_meta_data():
    meta_data = []
    for symbol in get_symbols():
        if os.path.exists(os.path.join(DATA_DIR, 'stock_data/{}'.format(symbol))) and not os.path.isfile(os.path.join(DATA_DIR, 'stock_data/{}'.format(symbol))):
            if os.listdir(os.path.join(DATA_DIR, 'stock_data/{}'.format(symbol))):
                with open(os.path.join(DATA_DIR, 'stock_data/{}/meta.pkl'.format(symbol)), "rb") as f:
                    meta = pickle.load(f)
                meta_data.append(meta)
    return meta_data


def get_names():
    names = []
    for meta in get_meta_data():
        names.append(meta.get('name'))
    return names


@app.route('/')
def home():
    return render_template('home.html', names=get_names())


@app.route('/industry')
def industry():
    return render_template('industry.html', names=get_names())


@app.route('/company')
def company():
    return render_template('company.html', names=get_names(), meta=get_meta_data())


class Scheduler(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        exec(open('data/data.py').read())


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)
