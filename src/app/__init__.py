from flask import Flask
from flask_login import LoginManager
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login' # view function that handles logins
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# This bottom import is a workaround to circular imports,
# a common problem with Flask applications.
# Routes module needs to import the app variable defined in this script,
# so putting one of the reciprocal imports at the bottom avoids the error
# that results from the mutual references between these two files.

from app import routes, models