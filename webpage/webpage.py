from flask import Flask, flash, redirect, render_template, request, \
                    session, url_for
import os

app = Flask(__name__)
app.secret_key = os.urandom(12)


@app.route('/index')
def welcome():
    if session.get('logged_in'):
        return render_template('index.html')
    else:
        flash('You are not authorized')
        return redirect(url_for('home'))


@app.route('/')
def home():
    if session.get('logged_in'):
        return redirect(url_for('welcome'))
    else:
        return render_template('login.html')


@app.route('/login', methods=['POST', 'GET'])
def do_login():
    if request.method == 'POST':
        if (request.form['password'] == '123' and
                request.form['username'] == 'adm'):
            session['logged_in'] = True
        else:
            flash('wrong password!')
    return home()


@app.route('/logout', methods=['GET'])
def do_logout():
    session['logged_in'] = False
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)
