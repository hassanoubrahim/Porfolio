from flask import Flask, flash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_redmail import RedMail
from flask_qrcode import QRcode
from dotenv import load_dotenv
load_dotenv()
import os

base_url = os.getenv("BASE_URL")

app = Flask(__name__, static_folder="../static")
qrcode = QRcode(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '$6552BDc3487TTrsdeOIIIEeueb$'

# RedMail configs
app.config["EMAIL_HOST"] = os.getenv('MAIL_SERVER')
app.config["EMAIL_PORT"] = os.getenv('MAIL_PORT')
app.config["EMAIL_USERNAME"] = os.getenv('MAIL_USERNAME')
app.config["EMAIL_PASSWORD"] = os.getenv('MAIL_PASSWORD')
app.config["EMAIL_SENDER"] = os.getenv('MAIL_USERNAME')
email = RedMail(app)

# Flask Mail Configs
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)

db = SQLAlchemy(app)

# create tables
@app.before_first_request
def create_tables():
    db.create_all()
