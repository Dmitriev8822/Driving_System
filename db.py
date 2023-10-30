from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

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


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=False)
    data = db.Column(db.String(128), nullable=False, unique=False)
    status = db.Column(db.String(128), nullable=False, unique=False)
    student_id = db.Column(db.String(128), nullable=False, unique=False)
    instructor_id = db.Column(db.String(128), nullable=False, unique=False)


def user_registration(login, password, user_type, name=None, second_name=None, father_name=None):
    res = User.query.filter_by(login=login).first()
    if res is None:
        user = User(login=login, password=password, user_type=user_type, \
                    name=name, second_name=second_name, father_name=father_name)
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


def users_data():
    res = [[str(user.id), str(user.login)] for user in User.query.filter_by(user_type='instructor').all()]
    return res


def create_users(num):
    cnt = 1
    for i in range(num):
        login = 'user' + str(cnt)
        cnt += 1
        res = -1
        while res != 0:
            res = user_registration(login=login, password='1234', user_type='instructor')


def delete_users():
    users = [user.id for user in User.query.all()]
    for id in users:
        User.query.filter_by(id=id).delete()
        db.session.commit()
