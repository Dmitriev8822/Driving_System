from flask import request, render_template, redirect, flash, url_for
from flask_login import login_required, logout_user, current_user

from main import app
from db import *


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    login = request.form.get('login')
    password = request.form.get('password')

    if request.method == 'POST':
        if not (login and password):
            flash('Fields must be fill')
        else:
            res = user_registration(login=login, password=password, user_type='student')
            if res == 0:
                return redirect(url_for('sign_in'))
            elif res == 1:
                flash('User already registered')
            else:
                flash('Something went wrong')

    return render_template('sign_up.html')


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    login = request.form.get('login')
    password = request.form.get('password')

    if request.method == 'POST':
        if not (login and password):
            flash('Fields must be fill.')
        else:
            res = user_authorization(login=login, password=password)
            if res == 0:
                return redirect(url_for('mpl'))
            elif res == 1:
                flash('User not found.')
            elif res == 2:
                flash('Password incorrect')

    return render_template('sign_in.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def user_logout():
    logout_user()
    return redirect('mp')


@app.after_request
def redirect_sing_in(response):
    if response.status_code == 401:
        return redirect('sign_in')
    return response


@app.route('/')
@app.route('/mp')
def mp():
    return render_template('mp.html')


@app.route('/mpl')
@login_required
def mpl():
    return render_template('mpl.html')


if __name__ == '__main__':
    app.run(debug=True)
