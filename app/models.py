from . import db
from werkzeug.security import generate_password_hash


class User(db.Model):
    __tablename__ = 'dd_user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(255))

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support

    def __repr__(self):
        return '<User %r>' % (self.username)


class Profile(db.Model):
    __tablename__ = 'dd_profile'

    id = db.Column(db.Integer, primary_key=True)
    phone_id = db.Column(db.String(255), unique=True)
    gender = db.Column(db.Integer)
    extraversion = db.Column(db.Integer)
    agreeableness = db.Column(db.Integer)
    conscientiousness = db.Column(db.Integer)
    emotional_stability = db.Column(db.Integer)
    intellect_imagination = db.Column(db.Integer)

    def __init__(self, phone_id, gender):
        self.phone_id = phone_id
        self.gender = gender


class Phone(db.Model):
    __tablename__ = 'dd_phone'

    id = db.Column(db.Integer, primary_key=True)
    phone_id = db.Column(db.String(255), unique=True)
    os_version = db.Column(db.String(50))
    cpu_utilization = db.Column(db.Integer)
    memory_utilization = db.Column(db.Integer)
    running_apps = db.Column(db.Integer)
    battery_percentage = db.Column(db.Integer)
    battery_state = db.Column(db.Integer)
    phone_model = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime)


class UserPhone(db.Model):
    """Connects User and Phone."""

    __tablename__ = 'dd_user_xphone'

    id = db.Column(db.Integer, primary_key=True)
    phone_id = db.Column(db.String(255))
    username = db.Column(db.String(80))


class AppPackageCategory(db.Model):
    __tablename__ = 'dd_app_package_category'

    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(100))
    package_name = db.Column(db.String(100))
    category = db.Column(db.String(50))


class RunningApps(db.Model):
    """Running Apps from Phone table connecting to App Pkg. Cat.."""

    __tablename__ = "dd_running_apps"

    id = db.Column(db.Integer, primary_key=True)
    running_apps = db.Column(db.Integer)
    app_pkg_cat = db.Column(db.Integer)

class AppUsage(db.Model):
    """App Usage for user."""

    __tablename__ = "dd_app_usage"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    app_pkg_cat = db.Column(db.Integer)
    time_sec = db.Column(db.Integer)
