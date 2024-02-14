import datetime
from datetime import date
from calendar import monthrange, month_name

from flask import request, render_template, redirect, flash, url_for
from flask_login import login_required, logout_user, current_user

import os
from PIL import Image, ImageDraw

from main import app
from db import *

app.config['SESSION_COOKIE_SECURE'] = True
path_to_profile_images = os.path.join('static', 'data', 'profile')
path_to_cars_images = os.path.join('static', 'data', 'cars')


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
        if user_id == file.split('.')[-2]:
            if change:
                os.remove(os.path.join(path_to_profile_images, f'{file}'))
                os.remove(os.path.join(path_to_profile_images, f'{user_id}r.png'))

            if path:
                if round_image:
                    return os.path.join(path_to_profile_images, user_id + 'r.' + file.split('.')[-1])
                else:
                    return os.path.join(path_to_profile_images, file)

            return True
    return False


def format_profile_photo(file):
    path_to_file = os.path.join(path_to_profile_images, file)
    image = Image.open(path_to_file)
    resized_image = image.resize((200, 200))
    os.remove(path_to_file)
    path_to_file = os.path.join(path_to_profile_images, file.split('.')[0] + '.' + 'png')
    resized_image.save(path_to_file)

    # Открываем изображение
    image = Image.open(path_to_file)
    image = image.resize((100, 100))
    rounded_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(rounded_image)
    draw.ellipse([(0, 0), image.size], fill=(255, 255, 255, 255))
    rounded_image.paste(image, (0, 0), mask=rounded_image)
    path_to_file = os.path.join(path_to_profile_images, file.split('.')[0] + 'r' + '.' + 'png')
    rounded_image.save(path_to_file)


def format_car_photo(file):
    path_to_file = os.path.join(path_to_cars_images, file)
    image = Image.open(path_to_file)
    resized_image = image.resize((640, 400))
    os.remove(path_to_file)
    path_to_file = os.path.join(path_to_cars_images, file.split('.')[0] + '.' + 'jpg')
    resized_image.save(path_to_file)


@app.route('/account/student_old', methods=['GET', 'POST'])
@login_required
def student_account_old():
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
        description = request.form.get('description')
        car_model = request.form.get('car_model')
        photo = request.files.get('photo')
        photo_car = request.files.get('photo_car')

        if fio and not fio.isspace() and len(fio.split()) == 3:
            second_name, name, father_name = fio.split()
            update_user_info(str(current_user.id), name=name, second_name=second_name, father_name=father_name)
        else:
            # вывод сообщения о некорректном вводе фио
            print('error')

        update_user_info(str(current_user.id), description=description, car=car_model)

        if photo is not None and photo.filename != '':
            is_profile_image(current_user.id, change=True)

            photo.filename = f'{str(current_user.id)}.png'
            photo.save(os.path.join(path_to_profile_images, photo.filename))

            format_profile_photo(photo.filename)

        if photo_car is not None and photo_car.filename != '':
            photo_car.filename = f'{str(current_user.id)}.jpg'
            photo_car.save(os.path.join(path_to_cars_images, photo_car.filename))
            format_car_photo(photo_car.filename)

    fio = ' '.join([current_user.name, current_user.second_name,
                    current_user.father_name]) if current_user.name is not None and current_user.second_name is not None and current_user.father_name is not None else ''

    user_id = str(current_user.id)
    car_model = current_user.car if current_user.car else ''
    description = current_user.description if current_user.description is not None else ''

    main_photo = os.path.join('..', is_profile_image(str(current_user.id),
                                                     path=True)) if current_user.is_authenticated and is_profile_image(
        str(current_user.id)) else '../static/img/photo.jpg'

    find_photo = list(filter(lambda img: img != None, [img if user_id == img.split('.')[0] else None for img in
                                                       os.listdir(path_to_cars_images)]))
    car_photo = os.path.join('..', path_to_cars_images, find_photo[0]) if find_photo else '../static/img/bigPhoto.jpg'

    return render_template('survey_instructor.html', fio=fio, description=description, user_id=user_id,
                           main_photo=main_photo, car=car_model, car_photo=car_photo)


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

            photo.filename = f'{str(current_user.id)}.png'
            photo.save(os.path.join(path_to_cars_images, photo.filename))

            format_profile_photo(photo.filename)

    fio = ' '.join([current_user.second_name, current_user.name,
                    current_user.father_name]) if current_user.name is not None and current_user.second_name is not None and current_user.father_name is not None else ''
    user_id = str(current_user.id)
    description = current_user.description if current_user.description is not None else ''
    # main_photo = '../' + path_to_profile_images + list(filter(lambda x: x != '', [name if user_id == name.split('.')[-2] else '' for name in os.listdir(path_to_profile_images)]))[0] if current_user.is_authenticated and is_profile_image(str(current_user.id)) else '../static/img/photo.jpg'
    main_photo = os.path.join('..', is_profile_image(str(current_user.id),
                                                     path=True)) if current_user.is_authenticated and is_profile_image(
        str(current_user.id)) else '../static/img/photo.jpg'
    return render_template('survey_student.html', fio=fio, description=description, user_id=user_id,
                           main_photo=main_photo)


@app.route('/swap')
def swap():
    if current_user.is_authenticated:
        if current_user.user_type == 'student':
            return redirect('/account/student')
        else:
            return redirect('/account/instructor')

    return render_template('swap.html')


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        # ..\static\img\user.png
        print(is_profile_image(current_user.id, path=True, round_image=True))
        path_image = is_profile_image(current_user.id, path=True, round_image=True) if is_profile_image(
            current_user.id) else r'..\static\img\user.png'
        # path_image = r'..\static\img\user.png'
        return render_template('index.html', login=True, path_image=path_image)
    return render_template('index.html')


@app.route('/search')
def search():
    result = get_instructors_info()
    return render_template('search.html', users=result)


@app.route('/calendar/<instructor_id>|<calendar_date>', methods=['GET', 'POST'])
@login_required
def calendar(instructor_id, calendar_date):
    if request.method == 'POST':
        instructor_id = request.form.get('instructor_id')
        lesson_date = request.form.get('lesson_date')
        work_time1 = request.form.get('workTime1')
        work_time2 = request.form.get('workTime2')
        meeting_place = request.form.get('meeting_place')
        lesson_price = request.form.get('lesson_price')
        print(instructor_id, lesson_date, work_time1, work_time2, meeting_place, lesson_price)

    if calendar_date == 'today':
        date_calendar = datetime.today()
    else:
        date_calendar = datetime.strptime(calendar_date, "%d%m%Y")

    last_week = (date_calendar - timedelta(7)).strftime("%d%m%Y")
    next_week = (date_calendar + timedelta(7)).strftime("%d%m%Y")

    year_today = date_calendar.year
    month_today = date_calendar.month if int(date_calendar.day) - int(
        date_calendar.weekday()) > 0 else date_calendar.month - 1
    day_today = int(date_calendar.day) - int(date_calendar.weekday()) if int(date_calendar.day) - int(
        date_calendar.weekday()) > 0 else int(monthrange(year_today, month_today)[1]) - (
            int(date_calendar.weekday()) - int(date_calendar.day))

    dt = date(
        year=year_today,
        month=month_today,
        day=day_today
    )

    dt7 = dt + timedelta(days=7)

    days = list()
    dates = list()

    while 1:
        if dt == dt7:
            break

        days.append(dt.day)
        dates.append(dt.strftime("%d.%m.%Y"))
        dt = dt + timedelta(1)

    dt -= timedelta(7)

    times = get_info_user_calendar(current_user.id, dt, dt7)

    return render_template('calendar.html', times=times, days=days, dates=dates, last_week=last_week, next_week=next_week, year=year_today, month=month_name[int(month_today)], instructor_id=instructor_id)


if __name__ == '__main__':
    # delete_users()
    app.run(debug=True)
