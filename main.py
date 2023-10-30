from flask import Flask

app = Flask(__name__)

app.secret_key = 'gZ6TeW@b&2@w%gc##2Y2rXe89J5rBu'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.app_context().push()