import os
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DB = os.getenv('MYSQL_DB')
MYSQL_PORT = os.getenv('MYSQL_PORT')

mysql = MySQL()
db = SQLAlchemy()


def init_mysql(app):
    app.config['MYSQL_HOST'] = MYSQL_HOST
    app.config['MYSQL_USER'] = MYSQL_USER
    app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
    app.config['MYSQL_DB'] = MYSQL_DB
    mysql.init_app(app)


def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
