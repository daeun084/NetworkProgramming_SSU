import random
import uuid

from flask import Flask, request, url_for, session, render_template, get_flashed_messages, flash, \
    jsonify
from jinja2 import Environment, FileSystemLoader
import game_db

app = Flask(__name__)
get = Environment(loader=FileSystemLoader('templates')).get_template
app.secret_key = str(uuid.uuid4())

# comment for client
win_comment = 'Congratulations, you did it.\n'
up_comment = 'Hint: You Guessed too high!\n'
down_comment = 'Hint: You guessed too small!\n'
attempt_comment = "Sorry, you've used all your attempts!\n"

# var for client's attemp and random number
game_attempts = 0
x = 0


# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if client request get methodm reder the login page
    if request.method == 'GET':
        return render_template('login.html')

    # get user information from json
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    if request.method == 'POST':
        # implement hardcoded login
        if (username, password) in [('admin', '123'), ('daeun', '123'), ('user', '123')]:
            # set session information
            session['username'] = username
            # use csrf_token
            session['csrf_token'] = uuid.uuid4().hex

            # init db
            # if user doesn't have data for game, make new record
            db = game_db.open_database()
            game_db.add_game_information(db, username, password, 0)
            db.commit()
            db.close()

            # return redirect link with JSON format
            return jsonify({'redirect': url_for('game')})
    return jsonify({'ERROR': 'Invalid Credentials'}), 401


# logout
@app.route('/logout', methods=['POST'])
def logout():
    # get data from json
    data = request.get_json()
    # check csrf_token
    if data.get('csrf_token') != session['csrf_token']:
        return jsonify({'ERROR': 'Unauthorized'}), 403

    # logout
    session.pop('username', None)
    # return redirect link to login page with JSON format
    return jsonify({'redirect': url_for('login')})


# index
@app.route('/', methods=['GET'])
def game():
    # session doesn't have username, return error
    if 'username' not in session:
        return jsonify({'ERROR': 'Unauthorized'}), 403

    username = session.get('username')
    if not username:
        # if username is None, return login link for redirect
        return jsonify({'redirect': url_for('login')})

    # get information (score) of user
    game_information = game_db.get_game_information(game_db.open_database(), username)

    global x
    global game_attempts

    # if attempt is 0, make random number
    if game_attempts == 0:
        x = random.randint(1, 10)
    # render user's score, csrf_token, flash message to game.html
    return render_template('game.html', response=get_flashed_messages(),
                           information=game_information, csrf_token=session['csrf_token'])


# guess
@app.route('/guess', methods=['POST'])
def guess():
    # check session
    username = session.get('username')
    if not username:
        return jsonify({'redirect': url_for('login')})

    # get user's guess num from json
    data = request.get_json()
    guess = data.get('guess', '').strip()

    # check csrf_token
    if data.get('csrf_token', '') != session['csrf_token']:
        return jsonify({'ERROR': 'Unauthorized'}), 403

    # if guess is none, render game.html again.
    if guess:
        global game_attempts
        global x
        response = None

        # casting str to int
        try:
            guess = int(guess)
        except ValueError:
            game_attempts += 1
            response = 'Invalid guess entered. Try Again.'
            flash(response)
            return jsonify({'redirect': url_for('game')})

        # compare the guess num and the random num
        if guess == x:
            # save win comment to response
            response = win_comment
            game_attempts = 0

            # change user's score information.
            db = game_db.open_database()
            game_db.patch_game_information(db, username)
            db.commit()

        elif guess < x:
            # save down comment to response
            response = down_comment
            game_attempts += 1
        elif guess > x:
            # save up comment to response
            response = up_comment
            game_attempts += 1

        # if the attempt is over, reset the game
        if game_attempts == 5:
            game_attempts = 0
            response = attempt_comment

        # flash response and redirect game.html again.
        flash(response)
        return jsonify({'redirect': url_for('game')})

    # render game.html with flash message
    return render_template('game.html',
                       response=get_flashed_messages(), csrf_token=session['csrf_token'])


if __name__ == '__main__':
    app.debug = True
    app.run()
