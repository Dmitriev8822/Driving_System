import datetime
from datetime import date
from calendar import monthrange

from flask import request, render_template, redirect, flash, url_for
from flask_login import login_required, logout_user, current_user

import os
from PIL import Image, ImageDraw

from main import app
from db import *

app.config['SESSION_COOKIE_SECURE'] = True
path_to_profile_images = os.path.join('static', 'img', 'profile')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("index"))


@app.route('/logout', methods=['GET'])
def logout():
    user_logout()
    return redirect('/')


@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect('/account/student')

    if request.method == 'POST':
        # получаем данные и записываем в базу данных
        number = request.form.get('telnum')
        password = request.form.get('password')
        password_v = request.form.get('password_v')

        if number != '' and password != '' and password_v != '':
            if password == password_v:
                res = user_registration(login=number, password=password, user_type='student')
                if res == 0:
                    return redirect('/authorization')
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
                    return redirect('/account/instructor')
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
    if current_user.is_authenticated:
        if current_user.user_type == 'student':
            return redirect('/account/student')
        else:
            return redirect('/account/instructor')

    if request.method == 'POST':
        # получаем данные и проверяем
        number = request.form.get('telnum')
        password = request.form.get('password')

        if number != '' and password != '':
            res = user_authorization(login=number, password=password)
            if res == 0:
                if current_user.user_type == 'student':
                    return redirect('/account/student')
                else:
                    return redirect('/account/instructor')

            elif res == 2:
                flash('Password is incorrect')
            elif res == 1:
                flash('User not detected')
            else:
                flash('Unknown error')
        else:
            flash('Fields must be filled')

    return render_template('login.html')


@app.route('/account', methods=['GET', 'POST'])
def account():
    if current_user.user_type == 'student':
        return redirect('/account/student')
    else:
        return redirect('/account/instructor')


def is_profile_image(user_id, change=False, path=False, round_image=False):
    user_id = str(user_id)
    files = os.listdir(path_to_profile_images)
    for file in files:
        if user_id in file:
            if change:
                os.remove(path_to_profile_images + f'{file}')
                os.remove(path_to_profile_images + f'{user_id}r.png')

            if path:
                if round_image:
                    return path_to_profile_images + user_id + 'r.' + file.split('.')[-1]
                else:
                    return path_to_profile_images + file

            return True
    return False


def format_profile_photo(file):
    path_to_file = path_to_profile_images + file
    image = Image.open(path_to_file)
    resized_image = image.resize((200, 200))
    os.remove(path_to_file)
    path_to_file = path_to_profile_images + file.split('.')[0] + '.' + 'png'
    resized_image.save(path_to_file)

    # Открываем изображение
    image = Image.open(path_to_file)
    image = image.resize((100, 100))
    rounded_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(rounded_image)
    draw.ellipse([(0, 0), image.size], fill=(255, 255, 255, 255))
    rounded_image.paste(image, (0, 0), mask=rounded_image)
    path_to_file = path_to_profile_images + file.split('.')[0] + 'r' + '.' + 'png'
    rounded_image.save(path_to_file)


@app.route('/account/student', methods=['GET', 'POST'])
@login_required
def student_account():
    if request.method == 'POST':
        fio = request.form.get('fio')
        description = request.form.get('description')
        photo = request.files.get('photo')
        # print(f'fio = {fio}; fio_issp = {fio.isspace()}; fio_spl = {fio.split()}.')
        if fio and not fio.isspace() and len(fio.split()) == 3:
            second_name, name, father_name = fio.split()
            update_user_info(str(current_user.id), name=name, second_name=second_name, father_name=father_name)
        else:
            # вывод сообщения о некорректном вводе фио
            print('error')

        update_user_info(str(current_user.id), description=description)

        if photo is not None and photo.filename != '':
            is_profile_image(current_user.id, change=True)

            extension = photo.filename.rsplit('.')[-1].lower()
            photo.filename = f'{str(current_user.id)}.{extension}'
            photo.save(path_to_profile_images + photo.filename)

            format_profile_photo(photo.filename)

    name = current_user.name if current_user.name is not None else ''
    user_id = str(current_user.id)
    fio = ' '.join([current_user.second_name, current_user.name,
                    current_user.father_name]) if current_user.name is not None else ''
    description = current_user.description if current_user.description is not None else ''
    main_photo = '../' + path_to_profile_images + \
                 [name if user_id in name else '' for name in os.listdir(path_to_profile_images)][
                     0] if current_user.is_authenticated and is_profile_image(
        str(current_user.id)) else '../static/img/photo_test.png'

    return render_template('student_account.html', fio=fio, description=description, name=name, user_id=user_id,
                           main_photo=main_photo)


@app.route('/account/instructor', methods=['GET', 'POST'])
@login_required
def instructor_account():
    if request.method == 'POST':
        fio = request.form.get('fio')

    return render_template('instructor_account.html')


@app.route('/swap')
def swap():
    return render_template('swap.html')


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        # ..\static\img\user.png
        path_image = is_profile_image(current_user.id, path=True, round_image=True) if is_profile_image(
            current_user.id) else r'..\static\img\user.png'
        # path_image = r'..\static\img\user.png'
        return render_template('index.html', login=True, path_image=path_image)
    return render_template('index.html')


@app.route('/search')
def search():
    result = get_instructors_info()
    return render_template('search.html', users=result)


@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    # if request.method == 'POST':
    #     name = request.form.get('')
    #     print(name)

    dates = list()
    # dt = datetime(year=2024, month=2, day=1)
    date_today = date.today()
    year_today = date_today.year
    month_today = date_today.month if int(date_today.day) - int(date_today.weekday()) > 0 else date_today.month - 1
    day_today = int(date_today.day) - int(date_today.weekday()) if int(date_today.day) - int(date_today.weekday()) > 0 else int(monthrange(year_today, month_today)[1]) - (int(date_today.weekday()) - int(date_today.day))
    # print(day_today)
    dt = date(
        year=year_today,
        month=month_today,
        day=day_today
    )

    dt7 = dt + timedelta(days=7)
    print(dt)
    print(dt7)
    while 1:
        if dt == dt7:
            break

        print(dates)
        dates.append(dt.day)
        dt = dt + timedelta(1)

    dt -= timedelta(7)

    times = get_info_user_calendar(current_user.id, dt, dt7)
    return render_template('data.html', times=times, dates=dates)


@app.route('/calendarw', methods=['GET', 'POST'])
def calendar_week():
    if request.method == 'POST':
        divinfo = request.get_json()
        print(divinfo)

    dates = list()
    # dt = datetime(year=2024, month=2, day=1)
    dt = date(
        year=date.today().year,
        month=date.today().month,
        day=int(date.today().day) - int(date.today().weekday())
    )

    dt7 = dt + timedelta(days=7)
    while 1:
        if dt == dt7:
            break

        dates.append(dt.day)
        dt = dt + timedelta(1)

    dt -= timedelta(7)

    times = get_info_user_calendar(current_user.id, dt, dt7)
    return render_template('data.html', times=times, dates=dates)


if __name__ == '__main__':
    # delete_users()
    app.run(debug=True)
