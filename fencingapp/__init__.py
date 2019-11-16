'''
instantiates objects for flask app, the database and the migration repository
'''
import logging
from logging.handlers import SMTPHandler
from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy # flask-sqlalchemy integration
from flask_migrate import Migrate       # handles migration of schmema changes to database
from flask_login import LoginManager    # handles user login management
from flask_bootstrap import Bootstrap
from config import Config


db = SQLAlchemy()      # create db object 

migrate = Migrate()   # database migration objects

login = LoginManager()   # login managmement object 
login.login_view = 'auth.login'  # defines the function in routes that handles user login
login.login_message = 'Please log in to access this page.'

bootstrap = Bootstrap()



def create_app(config_class=Config):
    '''
    Application factory to which initializes a flask app instance
    configures all the extensions to
    work with the instance and registers all the blueprints
    so that their components are included in the app
    It accepts a 
    '''
    app = Flask(__name__)  # creates a Flask object called app
    app.config.from_object(config_class)  # Defines location and type of database for the Flask app

    # initialize flask extensions
    db.init_app(app)
    migrate.init_app(app,db)
    login.init_app(app)
    bootstrap.init_app(app)

    # blueprint imports are done in the last possible moment
    # then each blueprint is registered with the Flask app object

    from fencingapp.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from fencingapp.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth') 

    from fencingapp.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:  # only send error emails if not in debug mode
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
                toaddrs=app.config['ADMINS'], subject='Fencing Manager Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)


    for k,v in app.config.items():
        print (k,':',v)
    return app


from fencingapp import models  # app.py contains all of the code for the endpoints of the routes used by Flask
                                             # import table schema from models.py module