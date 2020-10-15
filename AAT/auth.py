import functools
import pip._vendor.requests as requests

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)
from werkzeug.security import check_password_hash, generate_password_hash

from AAT.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        #get info from form submission
        password = request.form['password']
        #create connection with database
        db_conn = get_db()
        db = db_conn.cursor()
        #get authorization code in request parameters of URL
        authorization_code = request.args.get('code')
        #redirect to Zoom Oauth server if there's no authorization code
        # if authorization_code==None:
            # return redirect('https://zoom.us/oauth/authorize?response_type=code&client_id=' + request.env.clientID + '&redirect_uri=' + process.env.redirectURL)
        #info for access token request to Zoom Oauth server
        URL = 'https://zoom.us/oauth/token?grant_type=authorization_code&code='+authorization_code+'&redirect_uri='+request.base_url
        auth_headers = {
            "Authorization": "Basic MURIQTJpWUxTWGV4ZFY3dEF4bEJCQToyR3F1ZjBBQ0prTUpORUtVNGU4RXJrcVZMelFOTUdvMA==",
        }
        error = None
        #storing authorization response in local variables
        auth_response = requests.post(URL, headers=auth_headers)
        access_token = auth_response.json()['access_token']
        refresh_token = auth_response.json()['refresh_token']
        #use access token to request zoom account info
        request_headers = {
            "Authorization": "Bearer "+access_token,
        }
        user_response = requests.get('https://api.zoom.us/v2/users/me', headers=request_headers)
        name = user_response.json()['first_name']+" "+user_response.json()['last_name']
        email = user_response.json()['email'].lower()
        userID = user_response.json()['id']
        #check if all requests went through
        if auth_response.status_code!=200:
            error = "invalid authorization code"
        elif user_response.status_code!=200:
            error = "invalid user"
        else:
            db.execute('SELECT COUNT(email) FROM teacher WHERE email = %s;', (email,))
            if db.fetchone()[0] > 0:
                error = 'Email {} is already registered.'.format(email)
            
        if error is None:
            db.execute(
                'INSERT INTO teacher (accessToken, refreshToken, email, name, password, tardyTime, userID) VALUES (%s, %s, %s, %s, %s, %s, %s);',
                (access_token, refresh_token, email, name, generate_password_hash(password), 5, userID)
            )
            db_conn.commit()
            return redirect(url_for('auth.login'))

        flash(error)
    
    return render_template('auth/register.html')




@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        db = get_db().cursor()
        error = None
        db.execute(
            'SELECT * FROM teacher WHERE email = %s;', (email,)
        )
        user = db.fetchone()

        if user is None:
            error = 'Incorrect email address.'
        elif not check_password_hash(user[1], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['email'] = user[0]
            return redirect(url_for('account.details'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    email = session.get('email')

    if email is None:
        g.user = None
    else:
        db = get_db().cursor()
        db.execute(
            'SELECT * FROM teacher WHERE email = %s;', (email,)
        )
        g.user = db.fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
