"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db
from flask import (
    request, url_for, flash, jsonify, g,
    abort
)
from app.models import User, Profile, AppCategory, AppUsage, Recommendation
import os
import csv
import datetime
import pickle
import pandas as pd
import heapq
import random

# Using JWT
import jwt
from flask import _request_ctx_stack
from functools import wraps
import base64

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

@app.route('/api/test', methods=["GET", "POST"])
def test():
    return {"Test","hello"}

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
            profile = Profile(phone_id, gender, username)

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


@app.route('/api/usage', methods=["GET", "POST"])
@requires_auth
def log_usage():
    if request.method == "POST":
        user_app_usage = request.get_json()
        username = g.current_user.get("username", None)

        app_usage_obj = []
        if username is not None:
            for app_usage in user_app_usage:
                app_name = app_usage.get("label")
                time_sec = app_usage.get("usage time")

                app_category = AppCategory.query.filter_by(app_name=app_name).first()
                category = "Uncategorized"
                if app_category is not None:
                    category = app_category.category

                use_ts = app_usage.get("last time used")
                timestamp = datetime.datetime.fromtimestamp(int(use_ts) / 1000)
                app_obj = AppUsage(
                    username=username, category=category, time_sec=time_sec, timestamp=timestamp
                    )
                app_usage_obj+=[app_obj]

            db.session.add_all(app_usage_obj)
            db.session.commit()
            return {'data': 'Accepted'}, 201
        else:
            abort(400)

    if request.method == "GET":
        username = g.current_user.get("username", None)

        conscientiousness = pickle.load(
            open(
                '{}{}app{}static{}algorithms{}conscientiousness.pkl'.format(
                    os.getcwd(), os.sep, os.sep, os.sep, os.sep
                ), 'rb'
                )
            )
        agreeableness = pickle.load(
            open(
                '{}{}app{}static{}algorithms{}agreeableness.pkl'.format(
                    os.getcwd(), os.sep, os.sep, os.sep, os.sep
                ), 'rb'
                )
            )
        emotional_stability = pickle.load(
            open(
                '{}{}app{}static{}algorithms{}emotional_stability.pkl'.format(
                    os.getcwd(), os.sep, os.sep, os.sep, os.sep
                ), 'rb'
                )
            )
        extraversion = pickle.load(
            open(
                '{}{}app{}static{}algorithms{}extraversion.pkl'.format(
                    os.getcwd(), os.sep, os.sep, os.sep, os.sep
                ), 'rb'
                )
            )
        intellect_imagination = pickle.load(
            open(
                '{}{}app{}static{}algorithms{}intellect_imagination.pkl'.format(
                    os.getcwd(), os.sep, os.sep, os.sep, os.sep
                ), 'rb'
                )
            )

        app_cats = AppCategory.query.all()
        categories = [c.category for c in app_cats]
        categories+=['Uncategorized']

        user_complete = {}
        user_complete.update(dict(zip(categories, (0 for n in range(len(categories))))))

        user_usage_db = AppUsage.query.filter_by(username=username).all()
        
        for use_entry in user_usage_db:
            app_category = use_entry.category
            category_usage = use_entry.time_sec

            if user_complete[app_category] > 0:
                user_complete[app_category]+= category_usage
            else:
                user_complete[app_category] = category_usage

        user_dataset = [0, 0, 0, 0, 0]
        user_dataset+= user_complete.values()
        user_df = pd.DataFrame(user_dataset)
        user_df = user_df.transpose()

        pred_consc = conscientiousness.predict(user_df)
        pred_agree = agreeableness.predict(user_df)
        pred_emotion = emotional_stability.predict(user_df)
        pred_extra = extraversion.predict(user_df)
        pred_intellect = intellect_imagination.predict(user_df)

        user_profile = Profile.query.filter_by(username=username).first()

        user_profile.conscientiousness = float(pred_consc[0])
        user_profile.agreeableness = float(pred_agree[0])
        user_profile.emotional_stability = float(pred_emotion[0])
        user_profile.extraversion = float(pred_extra[0])
        user_profile.intellect_imagination = float(pred_intellect[0])
        db.session.commit()

        return {
            'data': {
                'conscientiousness': '{}'.format(pred_consc[0]),
                'agreeableness': '{}'.format(pred_agree[0]),
                'emotional_stability': '{}'.format(pred_emotion[0]),
                'extraversion': '{}'.format(pred_extra[0]),
                'intellect_imagination': '{}'.format(pred_intellect[0])
                }
            }
    else:
        abort(400)


@app.route('/api/recommendation/simple', methods=["GET", "POST"])
@requires_auth
def simple_suggestion():
    if request.method == 'GET':
        username = g.current_user.get("username", None)

        if username is not None:
            profile = Profile.query.filter_by(username=username).first()
            traits_lst = [
                profile.extraversion, # 0
                profile.agreeableness, # 1
                profile.conscientiousness, # 2
                profile.emotional_stability, # 3
                profile.intellect_imagination # 4
            ]

            dom_traits = heapq.nlargest(3, traits_lst)
            recommendation_pool = []
            fetch_lst = []

            for trait in dom_traits:
                fetch_lst+= [traits_lst.index(trait)]

            for fetch_r in fetch_lst:
                title = None
                if fetch_r == 0:
                    title = "Extraversion"
                if fetch_r == 1:
                    title = "Agreeableness"
                if fetch_r == 2:
                    title = "Conscientiousness"
                if fetch_r == 3:
                    title = "Emotional Stability"
                if fetch_r == 4:
                    title = "Intellect Imagination"

                recommendation_pool+= [
                    Recommendation.query.filter_by(
                        title=title
                    ).all()
                ]
            chosen_recommd = recommendation_pool[
                random.randint(0, len(recommendation_pool) - 1)
            ]

            return {
                'data': '{}'.format(
                    chosen_recommd[0].details
                )
            }

    return "recommendation"

@app.route('/api/load/appcat')
def app_cat():
    """app_cat_csv = 'C:\\Users\\Lenovo\\Downloads\\dailydelightandroid\\capstone-backend\\app\\static\\csv\\app_cat.csv' """
    app_cat_csv = './app/static/csv/app_cat.csv'

    if os.path.exists(app_cat_csv):
        app_cat_ls = []
        with open(app_cat_csv, 'r', newline='', encoding="utf8") as _file:
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


<<<<<<< Updated upstream
@app.route('/api/load/recommd', methods=["GET", "POST"])
def man_recommd():
    if request.method == 'POST':
        recommendations_json = request.get_json()

        recommendations_lst = []
        for recommendations in recommendations_json:
            title = recommendations.get("title")
            details = recommendations.get("details")
            date = recommendations.get("date", None)
            points = recommendations.get("points", None)

            if date is None:
                date = datetime.datetime.now()
            if points is None:
                points = 0

            recommd_obj = Recommendation(
                title=title,
                details=details,
                date=date,
                points=points
            )
            recommendations_lst+=[recommd_obj]

        db.session.add_all(recommendations_lst)
        db.session.commit()
        return {'data': 'Success'}, 201


=======
>>>>>>> Stashed changes
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
