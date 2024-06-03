import bank
from flask import Flask, redirect, request, url_for
from jinja2 import Environment, PackageLoader

app = Flask(__name__)
get = Environment(loader=PackageLoader(__name__, 'tmp')).get_template


# support get and post methods
@app.route('/login', methods=['GET', 'POST'])
def login():
    # get username and password from login form
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    # redirect to index page and set cookie
    if request.method == 'POST':
        if (username, password) in [('brandon', '123'), ('sam', '456')]:
            response = redirect(url_for('index'))
            response.set_cookie('username', username)
            return response
    return get('login.html').render(username=username)


@app.route('/logout')
def logout():
    # redirect to login and set cookie
    response = redirect(url_for('login'))
    response.set_cookie('username', '')
    return response


@app.route('/')
def index():
    username = request.cookies.get('username')
    if not username:
        # if cookies are not available. redirect to login page
        return redirect(url_for('login'))
    # get payment for user from database
    payments = bank.get_payments_of(bank.open_database(), username)
    # print payment on index.html
    return get('index.html').render(payments=payments, username=username,
                                    flash_message=request.args.getlist('flash'))


@app.route('/pay', methods=['GET', 'POST'])
def pay():
    username = request.cookies.get('username')
    if not username:
        return redirect(url_for('login'))
    # get informs from pay.html
    account = request.form.get('account', '').strip()
    dollars = request.form.get('dollars', '').strip()
    memo = request.form.get('memo', '').strip()
    complaint = None

    if request.method == 'POST':
        if account and dollars and dollars.isdigit() and memo:
            # add payment to DB
            db = bank.open_database()
            bank.add_payment(db, username, account, dollars, memo)
            db.commit()
            return redirect(url_for('index', flash='Payment successful'))
        complaint = ('Dollars must be Integer' if not dollars.isdigit()
                     else 'Please fill in all three blanks')

    return get('pay.html').render(complaint=complaint, account=account, dollars=dollars, memo=memo)


if __name__ == '__main__':
    app.debug = True
    app.run()