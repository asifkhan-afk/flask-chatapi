from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from flask_migrate import Migrate
from .socket import socketio

db = SQLAlchemy()

#db is exported to it
from .views import views
from .models import User
    
DATABASE_NAME = "chatapp.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'jkjkldjsklfjaskljf'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_NAME}'
    
    # socketio = SocketIO(app)
    socketio.init_app(app)
    db.init_app(app)
    migrate=Migrate(app,db)
    
    app.register_blueprint(views,url_prefix='/api')

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app,socketio

def create_database(app):
    database_path = os.path.join(app.root_path, DATABASE_NAME)
    if not os.path.exists(database_path):
        db.create_all()
        print('Database created')

