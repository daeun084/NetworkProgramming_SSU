import random
import uuid

from flask import Flask, redirect, request, url_for, session, render_template, get_flashed_messages, abort, flash, \
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
game_attempts = 0
x = 0


@app.route('/login', methods=['GET', 'POST'])
def login():
    # get user information
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    if request.method == 'POST':
        # implement hardcoded login
        if (username, password) in [('admin', '123'), ('daeun', '123'), ('user', '123')]:
            session['username'] = username
            # use csrf_token
            session['csrf_token'] = uuid.uuid4().hex

            # init db
            db = game_db.open_database()
            game_db.add_game_information(db, username, password, 0)
            db.commit()
            db.close()

            # redirect
            return redirect(url_for('game'))
    return render_template('login.html', username=username)


@app.route('/logout', methods=['POST'])
def logout():
    if request.form.get('csrf_token') != session['csrf_token']:
        return jsonify({'ERROR': 'Unauthorized'}), 403

    # logout
    session.pop('username', None)
    # redirect to login page
    return redirect(url_for('login'))


@app.route('/')
def game():
    # session doesn't have username, return error
    if 'username' not in session:
        return jsonify({'ERROR': 'Unauthorized'}), 403

    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

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


@app.route('/guess', methods=['GET', 'POST'])
def guess():
    # check session
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    # get user's guess num
    guess = request.form.get('guess', '').strip()

    if request.method == 'POST':
        # check csrf_token
        if request.form.get('csrf_token') != session['csrf_token']:
            return jsonify({'ERROR': 'Unauthorized'}), 403

        # if guess is none, render game.html again.
        if guess :
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
                return redirect(url_for('game'))
                # return jsonify({'message': response}), 400

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
            return redirect(url_for('game'))
            # return jsonify({'message': response})

    return render_template('game.html',
                           response=get_flashed_messages(), csrf_token=session['csrf_token'])


if __name__ == '__main__':
    app.debug = True
    app.run()
