import os, pprint, sqlite3


def open_database(path = 'game.db'):
    # if game.db doesn't exist, make file
    new = not os.path.exists(path)
    # connect sqlite
    db = sqlite3.connect(path)

    # make game TABLE
    if new:
        c = db.cursor()
        c.execute('CREATE TABLE game ( id INTEGER PRIMARY KEY,'
                  ' username TEXT NOT NULL, password TEXT, score INTEGER)')
    return db


def add_game_information(db, username, password, score):
    c = db.cursor()

    c.execute('SELECT * FROM game WHERE username = ?', (username,))
    user = c.fetchone()

    # if user is none, insert row with 0 score
    if user is None:
        c.execute('INSERT INTO game (username, password, score)'
              ' VALUES (?, ?, ?)', (username, password, score))


def patch_game_information(db, username, increment=1):
    # increase user's score 1
    c = db.cursor()
    c.execute('UPDATE game SET score = score + ? WHERE username = ?', (increment, username))


def get_game_information(db, username):
    c = db.cursor()

    # get user's information
    c.execute('SELECT * FROM game WHERE username = ? ORDER BY id', (username, ))

    row = c.fetchone()
    # return user's score only
    return row[3]


if __name__ == '__main__':
    db = open_database()