from flask import request, render_template, redirect, flash, url_for
from flask_login import login_required, logout_user, current_user

import os
from PIL import Image

from main import app
from db import *

app.config['SESSION_COOKIE_SECURE'] = True
path_to_profile_images = 'static/img/profile/'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


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
                    return redirect('/account/student')
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
    if request.method == 'POST':
        # получаем данные и проверяем
        number = request.form.get('telnum')
        password = request.form.get('password')

        if number != '' and password != '':
            res = user_authorization(login=number, password=password)
            if res == 0:
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


def is_profile_image(user_id, change=False):
    files = os.listdir(path_to_profile_images)
    for file in files:
        if user_id in file:
            if change:
                os.remove(path_to_profile_images + f'/{file}')
            return True
    return False


def format_profile_photo(file):
    path_to_file = path_to_profile_images + file
    image = Image.open(path_to_file)
    resized_image = image.resize((200, 200))
    os.remove(path_to_file)
    resized_image.save(path_to_file)

    # original_image = Image.open(image_path)
    # mask = Image.new("L", original_image.size, 0)
    # mask.paste(255, original_image.getroundrect((0, 0) + original_image.size, radius=100))
    # rounded_image = Image.new("RGBA", original_image.size)
    # rounded_image.paste(original_image, mask=mask)
    # rounded_image.save(output_path)


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
            is_profile_image(str(current_user.id), change=True)

            extension = photo.filename.rsplit('.')[-1].lower()
            photo.filename = f'{str(current_user.id)}.{extension}'
            photo.save(path_to_profile_images + photo.filename)

            format_profile_photo(photo.filename)

    name = current_user.name if current_user.name is not None else ''
    user_id = str(current_user.id)
    fio = ' '.join([current_user.second_name, current_user.name,
                    current_user.father_name]) if current_user.name is not None else ''
    description = current_user.description if current_user.description is not None else ''
    main_photo = '../' + path_to_profile_images + [name if user_id in name else '' for name in os.listdir(path_to_profile_images)][0] if current_user.is_authenticated and is_profile_image(str(current_user.id)) else '../static/img/photo_test.png'

    return render_template('student_account.html', fio=fio, description=description, name=name, user_id=user_id, main_photo=main_photo)


@app.route('/account/instructor', methods=['GET', 'POST'])
@login_required
def instructor_account():
    if request.method == 'POST':
        pass

    return render_template('instructor_account.html')


@app.route('/swap')
def swap():
    return render_template('swap.html')


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        print(current_user.id)
    return render_template('index.html')


if __name__ == '__main__':
    # delete_users()
    app.run(debug=True)
