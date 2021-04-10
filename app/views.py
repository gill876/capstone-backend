"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, auth
from flask import (
    render_template, request, url_for, flash, jsonify, g,
    abort
)
from app.forms import LoginForm
from app.models import User, Profile


###
# Routing for your application.
###
@auth.verify_password
def verify_password(username, password):
    # first try to authenticate by token
    auth = request.headers.get('Authorization', None)
    username = request.json.get('username')
    password = request.json.get('password')

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

    user = User.verify_auth_token(token)
    if user is not None:
        user = User.query.filter_by(username=username).first()
        if user is None:
            return False
    g.user = user
    return True


@app.route('/api/resource')
@auth.login_required
def get_resource():
    # return render_template('secure_page.html')
    return jsonify({'data': 'Hello, %s!' % g.user.username})


@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


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
            return {
                'user_id': user.id,
                'token': user.generate_auth_token(600).decode('ascii')
                }, 200

    return {"data": "Authentication failed"}, 404

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


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
