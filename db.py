from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

from datetime import datetime, timedelta

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
    car = db.Column(db.String(255), nullable=True, unique=False)

    # id_user || login || password || user_type || name || second_name || father_name || description


class Lesson(db.Model):
    id_lesson = db.Column(db.Integer, primary_key=True, unique=False, autoincrement=True)
    date = db.Column(db.DateTime, nullable=False, unique=True)
    duration = db.Column(db.Integer, nullable=False, unique=False)
    status = db.Column(db.String(128), nullable=False, unique=False)  # free || during || busy || entry
    student_id = db.Column(db.String(128), nullable=False, unique=False)
    instructor_id = db.Column(db.String(128), nullable=False, unique=False)

    # id_lesson || date || duration || status || student_id || instructor_id


class Cars(db.Model):
    id_car = db.Column(db.Integer, primary_key=True, unique=False, autoincrement=True)
    make = db.Column(db.String(128), nullable=False, unique=False)
    model = db.Column(db.String(128), nullable=False, unique=False)
    transmission = db.Column(db.String(128), nullable=False, unique=False)
    date_release = db.Column(db.String(128), nullable=False, unique=False)

    # id_car || make || model || transmission || date_release


def user_registration(login, password, user_type, name=None, second_name=None, father_name=None, description=None, car=None):
    res = User.query.filter_by(login=login).first()
    if res is None:
        user = User(login=login, password=password, user_type=user_type, \
                    name=name, second_name=second_name, father_name=father_name, description=description, car=car)
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
    users = [user.id_user for user in User.query.all()]
    for id in users:
        User.query.filter_by(id=id).delete()
        db.session.commit()


def update_user_info(user_id, login=None, password=None, user_type=None, name=None, second_name=None, father_name=None,
                     description=None, car=None):
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
    if car is not None:
        user.car = car

    db.session.commit()


def get_instructors_info():
    instructors = User.query.filter_by(user_type='instructor').all()

    results = []
    for instructor in instructors:
        results.append([instructor.name + ' ' + instructor.father_name, instructor.description])

    return results


def add_car_to_cars_list(car):
    make, model, transmission, date_from, date_to = car.split('-')
    if date_to == 'pt':
        date_to = str(datetime.now().year)

    for date in range(int(date_from), int(date_to)):
        car_model = Cars(make=make, model=model, transmission=transmission, date_release=str(date))
        db.session.add(car_model)
        db.session.commit()


def get_info_user_calendar(user_id, date_from, date_to):
    user_id = str(user_id)
    date = date_from
    results = list()
    while date < date_to:
        times = ['7:00', '7:30', '8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00', '11:30',
                 '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30',
                 '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30']

        lessons = [f'{lesson.date.hour}:{lesson.date.minute:02d}' if date.year == lesson.date.year and date.month == lesson.date.month and date.day == lesson.date.day else None for lesson in Lesson.query.filter_by().all()]
        lessons = list(filter(None, lessons))

        durations = [[lesson.duration, lesson.student_id] if date.year == lesson.date.year and date.month == lesson.date.month and date.day == lesson.date.day else None for lesson in Lesson.query.filter_by().all()]
        durations = list(filter(None, durations))

        i = 0
        result = list()
        while i < len(times):
            time = times[i]
            if time in lessons:
                employment = 'busy'
                if durations[lessons.index(time)][1] == user_id:
                    employment = 'entry'

                counter = durations[lessons.index(time)][0]
                for j in range(counter + 1):
                    result.append([times[i + j], employment])
                i += counter
            else:
                result.append([time, 'free'])
            i += 1

        results.append(result)

        date += timedelta(days=1)

    return results

    # for i in range(len(times)):
    #     el = times[i]
    #     if el in lessons:
    #         for j in range(len(durations[])):
    #         result.append([el, 'busy'])
    #     else:
    #         result.append([el, 'free'])


if __name__ == '__main__':
    # dt = datetime(year=2024, month=2, day=1)
    # dt7 = dt + timedelta(days=7)
    # times = get_info_user_calendar(1, dt, dt7)
    # print(times)



    # Lesson.query.filter_by(id_lesson=1).delete()
    # db.session.commit()

    # dt = datetime(year=2024, month=2, day=5, hour=11, minute=30)
    # lesson = Lesson(date=dt, duration=2, status='busy', student_id=1, instructor_id=3)  # id_lesson || date || duration || status || student_id || instructor_id
    # db.session.add(lesson)
    # db.session.commit()
    #
    # user_registration(login='user1', password='123', user_type='student')  # id_user || login || password || user_type || name || second_name || father_name || description
    # user_registration(login='user2', password='123', user_type='student')
    # user_registration(login='user3', password='123', user_type='instructor')
    pass
