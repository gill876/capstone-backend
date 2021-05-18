"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, auth
from flask import (
    request, url_for, flash, jsonify, g,
    abort
)
from app.models import User, Profile, AppCategory
import os
import csv

# Using JWT
import jwt
from flask import _request_ctx_stack
from functools import wraps
import base64


###
# Routing for your application.
###
# @auth.verify_password
# def verify_password(username, password):
#     # first try to authenticate by token
#     auth = request.headers.get('Authorization', None)
#     username = request.json.get('username')
#     password = request.json.get('password')

#     if not auth:
#       return jsonify({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'}), 401

#     parts = auth.split()

#     if parts[0].lower() != 'bearer':
#       return jsonify({'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}), 401
#     elif len(parts) == 1:
#       return jsonify({'code': 'invalid_header', 'description': 'Token not found'}), 401
#     elif len(parts) > 2:
#       return jsonify({'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}), 401

#     token = parts[1]

#     user = User.verify_auth_token(token)
#     if user is not None:
#         user = User.query.filter_by(username=username).first()
#         if user is None:
#             return False
#     g.user = user
#     return True


def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.headers.get('Authorization', None)
    if not auth:
      return jsonify({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'}), 401

    parts = auth.split()

    if parts[0].lower() != 'bearer':
      return jsonify({'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}), 401
    elif len(parts) == 1:
      return jsonify({'code': 'invalid_header', 'description': 'Token not found'}), 401
    elif len(parts) > 2:
      return jsonify({'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}), 401

    token = parts[1]
    try:
         payload = jwt.decode(token, app.config['SALT'])

    except jwt.ExpiredSignature:
        return jsonify({'code': 'token_expired', 'description': 'token is expired'}), 401
    except jwt.DecodeError:
        return jsonify({'code': 'token_invalid_signature', 'description': 'Token signature is invalid'}), 401

    g.current_user = user = payload
    return f(*args, **kwargs)

  return decorated


@app.route('/api/resource')
# @auth.login_required
@requires_auth
def get_resource():
    # return render_template('secure_page.html')
    return jsonify({'data': 'Hello, %s!' % g.current_user})


@app.route('/')
def home():
    """Render website's home page."""
    return "Home"


@app.route('/api/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Get the username and password values from the form.
        response = {'resp': 'Username already used.'}, 403

        username = request.json.get('username')
        password = request.json.get('password')
        phone_id = request.json.get('phone_id')
        gender = request.json.get('gender')

        if username is None or password is None:
            abort(400)

        user = User.query.filter_by(username=username).first()

        if user is None:
            user = User(username=username)
            user.hash_password(password)
            profile = Profile(phone_id, gender)

            # Add User and Profile
            db.session.add(user)
            db.session.add(profile)
            db.session.commit()

            response = jsonify(
                {
                    'user_id': user.id,
                    'token': user.generate_auth_token(600).decode('ascii')
                }
                ), 201, \
                {'Location': url_for('get_user', id=user.id, _external=True)}

    return response

@app.route("/api/users/signin", methods=["GET", "POST"])
def get_user():
    if request.method == "POST":
        username = request.json.get('username')
        password = request.json.get('password')

        user = User.query.filter_by(username=username).first()
        pass_auth = user.verify_password(password)
        if user is None:
            abort(400)
        elif pass_auth:
            # return {
            #     'user_id': user.id,
            #     'token': user.generate_auth_token(600).decode('ascii')
            #     }, 200
            payload = {'id': user.id, 'username': user.username}
            token = jwt.encode(payload, app.config['SALT'], algorithm='HS256').decode('utf-8')
            g.username = user.username
            # return jsonify(data={'token': token}, message="Token Generated and User Logged In")
            return {
                'user_id': user.id,
                'token': token
                }, 200

    return {"data": "Authentication failed"}, 404

#remember to delete below endoint. Was only for testing
@app.route("/api/test", methods=["GET", "POST"])
def test():
    print("in server")
    if request.method == "GET":
        
        return {"status": "this api works"}

    return {"data": "Authentication failed"}, 404

# @app.route('/api/usage', methods=["GET", "POST"])
# @requires_auth
# def log_usage():
#     if request.method == "POST":
#         user_app_usage = request.get_json()
#         username = g.current_user.get("username", None)

#         if username is not None:
#             pass
#         else:
#             abort(400)
    
#     return username


@app.route('/api/load/appcat')
def app_cat():
    app_cat_csv = '{}{}app{}static{}csv{}app_cat.csv'.format(
        os.getcwd(), os.sep, os.sep, os.sep, os.sep
        )

    if os.path.exists(app_cat_csv):
        app_cat_ls = []
        with open(app_cat_csv, 'r', newline='') as _file:
            dict_reader = csv.DictReader(_file)
            counter = 0
            for row in dict_reader:
                if counter == 0:
                    pass
                else:
                    #app_cat_dict[row['V1']] = row['V3']
                    app_cat_ls+=[AppCategory(app_name=row['V1'], category=row['V3'])]
                counter+= 1
        
        db.session.add_all(app_cat_ls)
        db.session.commit()
        return {'data': 'Saved to db'}
    else:
        abort(404)

###
# The functions below should be applicable to all Flask apps.
###

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


# @app.after_request
# def add_header(response):
#     """
#     Add headers to both force latest IE rendering engine or Chrome Frame,
#     and also to cache the rendered page for 10 minutes.
#     """
#     response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
#     response.headers['Cache-Control'] = 'public, max-age=0'
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return "Not found", 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
