from flask import request, render_template, redirect, flash, url_for
from flask_login import login_required, logout_user, current_user

from main import app
from db import *


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        # получаем данные и записываем в базу данных
        number = request.form.get('telnum')
        password = request.form.get('password')
        password_v = request.form.get('password_v')
        if number != '' and password != '' and password_v != '':
            if password == password_v:
                res = user_registration(login=number, password=password, user_type='student')
                if res == 0:
                    # в будущем редирект в личный кабинет
                    return redirect('/')
                else:
                    flash('User is already registered')
            else:
                flash('Passwords don\'t match')
        else:
            flash('Fields must be filled')

    # print(f'number: {number};\npassword: {password};\npassword_v: {password_v};\npassword check: {password == password_v}.')

    return render_template('student_registration.html')


@app.route('/register/instructor', methods=['GET', 'POST'])
def register_instructor():
    if request.method == 'POST':
        # получаем данные и записываем в базу данных
        number = request.form.get('telnum')
        password = request.form.get('password')
        password_v = request.form.get('password_v')

        if number != '' and password != '' and password_v != '':
            if password == password_v:
                res = user_registration(login=number, password=password, user_type='instructor')
                if res == 0:
                    # в будущем редирект в личный кабинет
                    return redirect('/')
                else:
                    flash('User is already registered')
            else:
                flash('Passwords don\'t match')
        else:
            flash('Fields must be filled')

    # print(f'number: {number};\npassword: {password};\npassword_v: {password_v};\npassword check: {password == password_v}.')

    return render_template('instructor_registration.html')


@app.route('/authorization', methods=['GET', 'POST'])
def authorization():
    if request.method == 'POST':
        # получаем данные и проверяем
        number = request.form.get('telnum')
        password = request.form.get('password')

        if number != '' and password != '':
            res = user_authorization(login=number, password=password)
            if res == 0:
                # в будущем редирект в личный кабинет
                return redirect('/')
            elif res == 2:
                flash('Password is incorrect')
            elif res == 1:
                flash('User not detected')
            else:
                flash('Unknown error')
        else:
            flash('Fields must be filled')

    return render_template('login.html')


@app.route('/swap')
def swap():
    return render_template('swap.html')


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        login = current_user.login
        return render_template('index.html', login=login)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
