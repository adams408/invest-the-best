import pandas as pd
import os
import pickle

from flask import jsonify

from . import web

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "database")


@web.route('/api/company')
def company(symbol):
    if os.path.exists(os.path.join(DATA_DIR, "symbols.pickle")):
        with open(os.path.join(DATA_DIR, "symbols.pickle"), "rb") as f:
            symbols = pickle.load(f)
    symbol = symbols[0]
    return jsonify(pd.read_csv(os.path.join(DATA_DIR, "stock_data/{}.csv").format(symbol)).to_dict('list'))
