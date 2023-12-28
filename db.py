from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

from datetime import datetime

from main import app

login_manager = LoginManager(app)
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=False)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, unique=False)
    user_type = db.Column(db.String(64), nullable=False, unique=False)
    name = db.Column(db.String(255), nullable=True, unique=False)
    second_name = db.Column(db.String(255), nullable=True, unique=False)
    father_name = db.Column(db.String(255), nullable=True, unique=False)
    description = db.Column(db.TEXT(1010), nullable=True, unique=False)


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=False, autoincrement=True)
    data = db.Column(db.String(128), nullable=False, unique=False)
    status = db.Column(db.String(128), nullable=False, unique=False)
    student_id = db.Column(db.String(128), nullable=False, unique=False)
    instructor_id = db.Column(db.String(128), nullable=False, unique=False)


class Cars(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=False, autoincrement=True)
    make = db.Column(db.String(128), nullable=False, unique=False)
    model = db.Column(db.String(128), nullable=False, unique=False)
    transmission = db.Column(db.String(128), nullable=False, unique=False)
    date_release = db.Column(db.String(128), nullable=False, unique=False)


def user_registration(login, password, user_type, name=None, second_name=None, father_name=None, description=None):
    res = User.query.filter_by(login=login).first()
    if res is None:
        user = User(login=login, password=password, user_type=user_type, \
                    name=name, second_name=second_name, father_name=father_name, description=description)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            print('Error:', e)
            db.session.rollback()
            return -1  # error
    else:
        return 1  # user is already registered

    return 0  # all right


def user_authorization(login, password):
    user = User.query.filter_by(login=login).first()
    if user is not None:
        if password == user.password:
            login_user(user)
            return 0  # all right
        else:
            return 2  # password is incorrect
    else:
        return 1  # user not detected


def user_logout():
    logout_user()
    return 0  # all right


def delete_users():
    users = [user.id for user in User.query.all()]
    for id in users:
        User.query.filter_by(id=id).delete()
        db.session.commit()


def update_user_info(user_id, login=None, password=None, user_type=None, name=None, second_name=None, father_name=None,
                     description=None):
    user = User.query.get(user_id)

    if login is not None:
        user.login = login
    if password is not None:
        user.password = password
    if user_type is not None:
        user.user_type = user_type
    if name is not None:
        user.name = name
    if second_name is not None:
        user.second_name = second_name
    if father_name is not None:
        user.father_name = father_name
    if description is not None:
        user.description = description

    db.session.commit()


def get_instructors_info():
    instructors = User.query.filter_by(user_type='instructor').all()

    results = []
    for instructor in instructors:
        results.append([instructor.name + ' ' + instructor.father_name, instructor.description])

    return results


def create_users(num):
    cnt = 1
    for i in range(num):
        cnt += 1
        res = -1
        while res != 0:
            res = user_registration('Dmitrii' + str(cnt), '123', 'instructor', name='Дмитрий' + str(cnt),
                                    second_name='Дмитриев' + str(cnt), father_name='Владимирович' + str(cnt),
                                    description='Hi, I am nice teacher!' + str(cnt))
            cnt += 1


def add_car_to_cars_list(car):
    make, model, transmission, date_from, date_to = car.split('-')
    if date_to == 'pt':
        date_to = str(datetime.now().year)

    for date in range(int(date_from), int(date_to)):
        car_model = Cars(make=make, model=model, transmission=transmission, date_release=str(date))
        db.session.add(car_model)
        db.session.commit()


if __name__ == '__main__':
    add_car_to_cars_list('Lada-Vesta-R-2015-pt')
    pass
