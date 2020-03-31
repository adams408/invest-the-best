import pandas as pd

from flask import jsonify

from . import app


@app.route('/api/company')
def endpoint():

    return jsonify(pd.read_csv('src/group5/team_members.csv').to_dict('list'))