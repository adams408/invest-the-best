import threading

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/industry')
def industry():
    return render_template('industry.html')


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
