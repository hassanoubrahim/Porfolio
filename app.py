from flask import Flask, redirect, render_template, request, url_for
from core.routes import web
from core.routes import social_auth
from core.chars_regenerate import shorten_url_generate
from core import *
from flask_moment import Moment

moment = Moment(app)
moment = Moment()
moment.init_app(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
