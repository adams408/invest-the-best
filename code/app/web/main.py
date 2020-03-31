from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret.io'
socketio = SocketIO(app)


@app.route('/')
def home():
    return render_template('home.html')


# @code.route('/industry')
# def industry():
#     return render_template('industry.html')
#
#
# @code.route('/industry/company')
# def company():
#     return render_template('company.html')


@socketio.on('my event', namespace='/')
def test_message(message):
    emit('my response', {'database': message['database']})


@socketio.on('connect', namespace='/')
def test_connect():
    emit('my response', {'database': 'Connected'})


@socketio.on('disconnect', namespace='/')
def test_disconnect():
    print('client disconnected')


if __name__ == '__main__':
    socketio.run(app)
