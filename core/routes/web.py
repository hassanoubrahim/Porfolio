import json
import secrets
import httpagentparser
from urllib.request import urlopen
from flask import Flask, jsonify, redirect, render_template, request, url_for
from sqlalchemy import func
import validators
from core.greetings import fun_greetings
from models.base_model import User, Urls, Location
from core.chars_regenerate import shorten_url_generate
from flask_login import login_required, current_user
from core.auth import *
from core import *
from PIL import Image
from flask_mail import Message
import datetime
from authlib.integrations.flask_client import OAuth

from werkzeug.user_agent import UserAgent

oauth = OAuth(app)



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, '../static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        url_received = request.form["url"]
        found_url = Urls.query.filter_by(long=url_received).first()

        if found_url:
            # return redirect(url_for("display_short_url", url=found_url.short))
            # return found_url
            short_url = found_url.short
            # return jsonify({'output':'Your Name is ' + url_received + ', right?'})
        else:
            short_url = shorten_url_generate()
            print(short_url)
            if current_user.is_authenticated:
                user_id = current_user.id
            else:
                user_id = 0
            hits = 0
            new_url = Urls(user_id, url_received, short_url, hits)
            db.session.add(new_url)
            db.session.commit()
            # return redirect(url_for("display_short_url", url=short_url))
        return jsonify({'output': base_url + '/' + short_url})
        # return jsonify({'error' : 'Error!'})
    else:
        return render_template('index.html')

@app.route('/about-us')
def about():
    return render_template('about.html')

@app.route('/<short_url>')
def redirection(short_url):
    qry = Urls.query.filter_by(short=short_url).first()
    userInfo = httpagentparser.detect(request.headers.get('User-Agent'))
    # public_ip = "41.89.17.2"
    public_ip = request.remote_addr
    url = 'https://api.ipgeolocation.io/ipgeo?apiKey=3a97a60077094f69a3e34d6b2edc4f96&ip={}'.format(public_ip)
    response = urlopen(url)
    data = json.load(response)
    country = data['country_name']
    city = data['city']
    userPlatform = userInfo['platform']['name']
    userOs = userInfo['os']['name']
    userBrowser = userInfo['browser']['name']

    if qry:
        url_id =qry.id_
        hits =qry.hits
        qry.hits =  hits+1
        db.session.merge(qry)
        db.session.commit()

        user_location = Location(url_id, country, city, userPlatform, userOs, userBrowser, public_ip)
        db.session.add(user_location)
        db.session.commit()

        return redirect(qry.long)
    else:
        return f'<h1>Url doesnt exist</h1>'

@app.route('/my-urls/<int:page_num>')
@login_required
def myurls(page_num=1):
    myurls = db.session.query(User, Urls).join(Urls).filter_by(user_id = current_user.id).order_by(Urls.id_.desc()).paginate(per_page=5, page=page_num, error_out=True)
    count = db.session.query(Urls).filter_by(user_id = current_user.id).count()
    return render_template('all-urls.html', vals=myurls, base_url=base_url, count=count )

@app.route('/user-locations')
@login_required
def locations():
    return render_template('all-locations.html', vals=db.session.query(Location, Urls).join(Urls).filter_by(user_id = current_user.id).order_by(Location.id.desc()).all(), base_url=base_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(request.referrer)
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.username.data).first()
        login_method = user.login_method
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            
            elif(login_method != "email"):
                flash('Please login with {} or reset your password'.format(login_method), 'error')
            else:
                flash('Email or Password is incorrect', 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(name=form.name.data, email=form.email.data,image_file="default.jpg", login_method="email", password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('You have sucessfully Registered, Please Login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    count = db.session.query(Urls).filter_by(user_id = current_user.id).count()
    greeting = fun_greetings()
    loc = db.session.query(Location.city, Location.country, db.func.count(Location.city).label('count')).join(Urls).filter_by(user_id = current_user.id).group_by(Location.city).order_by(func.count().desc()).limit(5)
    platform = db.session.query(Location.platform, db.func.count(Location.platform).label('count')).join(Urls).filter_by(user_id = current_user.id).group_by(Location.platform).order_by(func.count().desc()).limit(5)
    browser = db.session.query(Location.browser, db.func.count(Location.browser).label('count')).join(Urls).filter_by(user_id = current_user.id).group_by(Location.browser).order_by(func.count().desc()).limit(5)
    os = db.session.query(Location.os, db.func.count(Location.os).label('count')).join(Urls).filter_by(user_id = current_user.id).group_by(Location.os).order_by(func.count().desc()).limit(5)
    top_hits = db.session.query(Urls).filter_by(user_id = current_user.id).order_by(Urls.hits.desc()).limit(5)
    # today_hits = db.session.query(func.sum(Urls.hits).label('sum')).filter_by(user_id = current_user.id).filter(Urls.created_at.date() == datetime.date.today()).first().sum
    total_hits = db.session.query(func.sum(Urls.hits).label('sum')).filter_by(user_id = current_user.id).first().sum

    validate_image_url=validators.url(current_user.image_file)
    if validate_image_url==True:
        image_file = current_user.image_file
    else:
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    
    return render_template('dashboard.html', title='Account',
                           image_file=image_file, form=form, link_count=count, greeting=greeting, loc=loc, platforms=platform, browsers=browser, uos=os, top_hits=top_hits, total_hits=total_hits, base_url=base_url)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=('Tinly','info@cloudrebue.co.ke'),
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)


@app.route("/reset-password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset-password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    # return user
    if user is None:
        flash('That is an invalid or expired token', 'error')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been sucessfully Logged out, Please Login again.', 'success')
    return redirect(url_for('login'))
