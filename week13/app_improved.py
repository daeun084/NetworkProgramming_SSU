import uuid

import bank
from flask import Flask, redirect, request, url_for, session, render_template, get_flashed_messages, abort, flash
from jinja2 import Environment, PackageLoader

app = Flask(__name__)
get = Environment(loader=PackageLoader(__name__, 'tmp')).get_template
# contain secret key for verifying session
app.secret_key = ''


# support get and post methods
@app.route('/login', methods=['GET', 'POST'])
def login():
    # get username and password from login form
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    # redirect to index page and set cookie
    if request.method == 'POST':
        if (username, password) in [('brandon', '123'), ('sam', '456')]:
            # set cookie using secret key when logging in
            session['username'] = username
            # generate random token
            session['csrf_token'] = uuid.uuid4().hex
            return redirect(url_for('index'))
    # provide automatic HTML escaping
    return render_template('login.html', username=username)


@app.route('/logout')
def logout():
    session.pop('username', None)
    # redirect to login
    return redirect(url_for('login'))


@app.route('/')
def index():
    # use key before trusting any cookie values
    username = session.get('username')
    if not username:
        # if session is not available. redirect to login page
        return redirect(url_for('login'))
    # get payment for user from database
    payments = bank.get_payments_of(bank.open_database(), username)
    # provide automatic HTML escaping
    # use internal storage for flashed messages
    return render_template('index.html', payments=payments, username=username,
                                    flash_message=get_flashed_messages())


@app.route('/pay', methods=['GET', 'POST'])
def pay():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    # get informs from pay.html
    account = request.form.get('account', '').strip()
    dollars = request.form.get('dollars', '').strip()
    memo = request.form.get('memo', '').strip()
    complaint = None

    if request.method == 'POST':
        # check token value for POST
        if request.form.get('csrf_token') != session['csrf_token']:
            abort(403)
        if account and dollars and dollars.isdigit() and memo:
            # add payment to DB
            db = bank.open_database()
            bank.add_payment(db, username, account, dollars, memo)
            db.commit()
            # no redirect containing flash
            flash('Payment successful')
            return redirect(url_for('index'))
        complaint = ('Dollars must be Integer' if not dollars.isdigit()
                     else 'Please fill in all three blanks')
    # provide automatic HTML escaping
    # return new session token
    return render_template('pay.html', complaint=complaint, account=account,
                           dollars=dollars, memo=memo,
                           csrf_token=session['csrf_token'])


if __name__ == '__main__':
    app.debug = True
    app.run()