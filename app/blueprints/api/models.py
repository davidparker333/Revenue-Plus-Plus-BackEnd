from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from datetime import date, datetime, timedelta
from sqlalchemy import desc
import os
import base64

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(32), index=True)
    token_expiration = db.Column(db.DateTime(), default=datetime.utcnow())
    leads = db.Relationship('Lead', backref='owner', lazy='dynamic')

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = generate_password_hash(password)

    def __repr__(self):
        return f'<User Object | {self.username}>'

    def __str__(self):
        return f'User - {self.id} - {self.username}'

    def get_token(self, expires_in=7200):
        now = datetime.utcnow()
        if self.token and self.token_expiration > (now + timedelta(seconds=60)):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        else:
            return user
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username
        }

    def from_dict(self, data):
        for field in ['email', 'password', 'username']:
            if field in data:
                setattr(self, field, data[field])



class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    cell_phone_number = db.Column(db.String(20))
    business_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    hot = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    open = db.Column(db.Boolean, nullable=False)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow())

    def __init__(self, first_name, last_name, phone_number, business_name, address, status, hot, user_id, open=True, cell_phone_number=None):
       self.first_name = first_name
       self.last_name = last_name
       self.phone_number = phone_number
       self.business_name = business_name
       self.address = address
       self.status = status
       self.hot = hot
       self.user_id = user_id
       self.open = open
       self.cell_phone_number = cell_phone_number

    def __repr__(self):
        return f'<Lead Object | {self.business_name}>'

    def __str__(self):
        return f'Post - {self.id} - {self.business_name}'

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "cell_phone_number": self.cell_phone_number,
            "business_name": self.business_name,
            "address": self.address,
            "status": self.address,
            "hot": self.hot,
            "date_created": self.date_created
        }

    def from_dict(self, data):
        for field in ['first_name', 'last_name', 'phone_number', 'cell_phone_number', 'business_name', 'address', 'status', 'hot']:
            if field in data:
                setattr(self, field, data[field])

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
