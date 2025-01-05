from platform import platform
from flask import jsonify
from sqlalchemy import DateTime, Integer
import json
import datetime
import jwt
from flask_login import UserMixin
from core import db, app

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(120), nullable=False, default='default.jpg')
    login_method = db.Column(db.String(20), nullable=False, default='email')
    password = db.Column(db.String(80), nullable=False)
    created_at = db.Column(DateTime, default=datetime.datetime.now)
    updated_at = db.Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def get_reset_token(self, expiration=300):
        reset_token = jwt.encode(
            {
                "user_id": self.id,
                "exp": datetime.datetime.utcnow()
                        + datetime.timedelta(seconds=expiration)
            }, 
        app.config['SECRET_KEY'],
        algorithm="HS256"
        )
        return reset_token

    @staticmethod
    def verify_reset_token(token):
        try:
            data = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                leeway=datetime.timedelta(seconds=10),
                algorithms=["HS256"]
            )
            user_id = jsonify(data['user_id'])
            # id = int(user_id)
            data_json = json.dumps(data)
            id  = data_json[12]
        except:
            return None
        return User.query.get(id)
        # return jsonify(data['user_id'])

    def __init__(self, name, email, image_file, login_method, password):
        self.name = name
        self.email = email
        self.image_file = image_file
        self.login_method = login_method
        self.password = password

class Urls(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.Integer, db.ForeignKey('user.id'), nullable=True, default=0)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(10), nullable=False, unique=True)
    hits = db.Column("hits", db.Integer, nullable=False, default=0)
    created_at = db.Column(DateTime, default=datetime.datetime.now)
    updated_at = db.Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, user_id, long, short, hits=0):
        self.user_id = user_id
        self.long = long
        self.short = short
        self.hits = hits

class Location(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    url_id = db.Column("url_id", db.Integer, db.ForeignKey('urls.id_'), nullable=False)
    country = db.Column("country", db.String(50))
    city = db.Column("city", db.String(10), nullable=False)
    platform = db.Column("platform", db.String(50))
    os = db.Column("os", db.String(50))
    browser = db.Column("browser", db.String(50))
    ip = db.Column("ip", db.String(50))
    created_at = db.Column(DateTime, default=datetime.datetime.now)
    updated_at = db.Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __init__(self, url_id, country, city, platform, os, browser, ip):
        self.url_id = url_id
        self.country = country
        self.city = city
        self.platform = platform
        self.os = os
        self.browser = browser
        self.ip = ip