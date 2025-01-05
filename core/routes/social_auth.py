import random
import string
from flask import Flask, render_template, request, url_for, redirect
from authlib.integrations.flask_client import OAuth
from core import *
from core.auth import *
from models.base_model import User

oauth = OAuth(app)

def get_random_string(size):
    chars = string.ascii_lowercase+string.ascii_uppercase+string.digits
    return ''.join(random.choice(chars) for _ in range(size))

google = oauth.register(
    name = 'google',
    client_id = os.getenv("GOOGLE_CLIENT_ID"),
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url = os.getenv("GOOGLE_SERVER_META_URI"),
    client_kwargs = {'scope': 'openid email profile'},
)


github = oauth.register (
  name = 'github',
    client_id = os.getenv("GITHUB_CLIENT_ID"),
    client_secret = os.getenv("GITHUB_CLIENT_SECRET"),
    access_token_url = 'https://github.com/login/oauth/access_token',
    access_token_params = None,
    authorize_url = 'https://github.com/login/oauth/authorize',
    authorize_params = None,
    api_base_url = 'https://api.github.com/',
    client_kwargs = {'scope': 'user:email'},
)


facebook = oauth.register(
    name='facebook',
    client_id = os.getenv('FACEBOOK_CLIENT_ID'),
    client_secret = os.getenv('FACEBOOK_CLIENT_SECRET'),
    access_token_url='https://graph.facebook.com/oauth/access_token',
    access_token_params=None,
    authorize_url='https://www.facebook.com/dialog/oauth',
    authorize_params=None,
    api_base_url='https://graph.facebook.com/',
    client_kwargs={'scope': 'email'},
)

# Google Login route
@app.route('/google/')
def google_login():
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)
 
@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    userinfo = oauth.google.parse_id_token(token, None)
    print(f"\n{userinfo}\n")
    # return userinfo["email"]

    # Create a user in your db with the information provided
    # by Github
    user = User.query.filter_by(email=userinfo["email"]).first()
    if user:
        login_user(user)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        
    # Create user and send user back to homepage
    new_user = User(name=userinfo["name"], email=userinfo["email"], image_file=userinfo["picture"], login_method="Google", password=bcrypt.generate_password_hash(get_random_string(20)))
    db.session.add(new_user)
    db.session.commit()
    user = User.query.filter_by(email=userinfo["email"]).first()
    login_user(user)
    return redirect(url_for("dashboard"))

# Github login route
@app.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)


# Github authorize route
@app.route('/github/auth/')
def github_authorize():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    userinfo = github.get('user').json()
    # print(f"\n{userinfo}\n")
    # return userinfo["name"]

    # Create a user in your db with the information provided
    # by Github
    user = User.query.filter_by(email=userinfo["email"]).first()
    if user:
        login_user(user)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        
    # Create user and send user back to homepage
    new_user = User(name=userinfo["name"], email=userinfo["email"], image_file=userinfo["avatar_url"], login_method="Github", password=bcrypt.generate_password_hash(get_random_string(20)))
    db.session.add(new_user)
    db.session.commit()
    user = User.query.filter_by(email=userinfo["email"]).first()
    login_user(user)
    return redirect(url_for("dashboard"))

@app.route('/twitter/')
def twitter():
   
    # Twitter Oauth Config
    TWITTER_CLIENT_ID = os.environ.get('TWITTER_CLIENT_ID')
    TWITTER_CLIENT_SECRET = os.environ.get('TWITTER_CLIENT_SECRET')
    oauth.register(
        name='twitter',
        client_id=TWITTER_CLIENT_ID,
        client_secret=TWITTER_CLIENT_SECRET,
        request_token_url='https://api.twitter.com/oauth/request_token',
        request_token_params=None,
        access_token_url='https://api.twitter.com/oauth/access_token',
        access_token_params=None,
        authorize_url='https://api.twitter.com/oauth/authenticate',
        authorize_params=None,
        api_base_url='https://api.twitter.com/1.1/',
        client_kwargs=None,
    )
    redirect_uri = url_for('twitter_auth', _external=True)
    return oauth.twitter.authorize_redirect(redirect_uri)
 
@app.route('/twitter/auth/')
def twitter_auth():
    token = oauth.twitter.authorize_access_token()
    resp = oauth.twitter.get('account/verify_credentials.json')
    profile = resp.json()
    print(" Twitter User", profile)
    return redirect('/')
 
@app.route('/login/facebook/')
def facebook_login():
    redirect_uri = url_for('facebook_auth', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)
 
@app.route('/facebook/auth/')
def facebook_auth():
    token = oauth.facebook.authorize_access_token()
    resp = oauth.facebook.get(
        'https://graph.facebook.com/me?fields=id,name,email,picture{url}')
    userinfo = resp.json()
    print("Facebook User ", userinfo)
    user = User.query.filter_by(email=userinfo["email"]).first()
    if user:
        login_user(user)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        
    # Create user and send user back to homepage
    new_user = User(name=userinfo["name"], email=userinfo["email"], image_file=userinfo["picture"]["data"]["url"], login_method="Facebook", password=bcrypt.generate_password_hash(get_random_string(20)))
    db.session.add(new_user)
    db.session.commit()
    user = User.query.filter_by(email=userinfo["email"]).first()
    login_user(user)
    return redirect(url_for("dashboard"))

