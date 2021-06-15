from . import bp as api
from app import db
from flask import jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.blueprints.api.models import User
from werkzeug.security import check_password_hash

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username, password):
    u = User.query.filter_by(username=username).first()
    if u and check_password_hash(u.password, password):
        return u

@token_auth.verify_token
def verify_token(token):
    if token:
        return User.check_token(token)
    return None

@api.route('/login', methods=['POST'])
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'token': token, 'expiration': user.token_expiration})