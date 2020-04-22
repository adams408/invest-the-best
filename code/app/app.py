import pandas as pd
import os
import pickle
import threading

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/industry')
def industry():
    if request.method == 'GET':
        return render_template('industry.html')
    if request.method == 'POST':
        if os.path.exists(os.path.join(DATA_DIR, "symbols.pickle")):
            with open(os.path.join(DATA_DIR, "symbols.pickle"), "rb") as f:
                symbols = pickle.load(f)
        symbol = symbols[0]
        return jsonify(pd.read_csv(os.path.join(DATA_DIR, "stock_data/{}.csv").format(symbol)).to_dict('list'))

        # return render_template('industry.html', data=data)


@app.route('/industry/company')
def company():
    return render_template('company.html')


class Scheduler(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        exec(open('data/data.py').read())


if __name__ == '__main__':
    # Scheduler().start()
    app.run(debug=True, host='127.0.0.1', port=8000)
