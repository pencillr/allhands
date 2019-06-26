from flask import Flask
from flask_login import LoginManager
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
import logging
from logging.handlers import SMTPHandler

app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login' # view function that handles logins
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
moment = Moment(app)

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

# This bottom import is a workaround to circular imports,
# a common problem with Flask applications.
# Routes module needs to import the app variable defined in this script,
# so putting one of the reciprocal imports at the bottom avoids the error
# that results from the mutual references between these two files.

from app import routes, models, errors