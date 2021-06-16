from sqlalchemy.sql.operators import op
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


# #############################################
#                  USER MODEL 
# #############################################

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(32), index=True)
    token_expiration = db.Column(db.DateTime(), default=datetime.utcnow())
    leads = db.relationship('Lead', backref='owner', lazy='dynamic')

    def __init__(self, email=None, username=None, password=None):
        self.email = email
        self.username = username
        self.password = password

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
                if field == 'password':
                    setattr(self, field, generate_password_hash(data[field]))
                else:
                    setattr(self, field, data[field])

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


# #############################################
#                  LEAD MODEL 
# #############################################

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    cell_phone_number = db.Column(db.String(20))
    business_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    hot = db.Column(db.Boolean(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    open = db.Column(db.Boolean(), nullable=False)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow())
    opportunity = db.relationship('Opportunity', backref='lead', lazy='dynamic')
    activity = db.relationship('Activity', backref='lead', lazy='dynamic')

    def __init__(self, first_name=None, last_name=None, phone_number=None, business_name=None, address=None, status=None, hot=None, user_id=None, open=True, cell_phone_number=None):
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
            "status": self.status,
            "hot": self.hot,
            "date_created": self.date_created
        }

    def from_dict(self, data):
        for field in ['first_name', 'last_name', 'phone_number', 'cell_phone_number', 'business_name', 'address', 'status', 'hot', 'user_id']:
            if field in data:
                setattr(self, field, data[field])

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def convert(self):
        opportunity = Opportunity()
        opportunity.first_name = self.first_name
        opportunity.last_name = self.last_name
        opportunity.phone_number = self.phone_number
        opportunity.cell_phone_number = self.cell_phone_number
        opportunity.business_name = self.business_name
        opportunity.address = self.address
        opportunity.status = "Meeting Scheduled"
        opportunity.value = 0
        opportunity.lead_id = self.id
        self.open = False
        opportunity.save()
        activities = Activity.query.filter(Activity.lead_id == self.id)
        for activity in activities:
            activity.opportunity_id = opportunity.id
            activity.save()

    

# #############################################
#             OPPORTUNITY MODEL 
# #############################################

class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    cell_phone_number = db.Column(db.String(20))
    business_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float(), nullable=False)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=False)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow())
    open = db.Column(db.Boolean(), nullable=False)
    event = db.relationship('Event', backref='opportunity', lazy='dynamic')
    activity = db.relationship('Activity', backref='opportunity', lazy='dynamic')

    def __init__(self, first_name=None, last_name=None, phone_number=None, business_name=None, address=None, status=None, value=None, lead_id=None, open=True, cell_phone_number=None):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.business_name = business_name
        self.address = address
        self.status = status
        self.value = value
        self.lead_id = lead_id
        self.open = open
        self.cell_phone_number = cell_phone_number

    def __repr__(self):
        return f'<Opportunity Object | {self.business_name}>'

    def __str__(self):
        return f'Opportunity - {self.id} - {self.business_name}'

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "cell_phone_number": self.cell_phone_number,
            "business_name": self.business_name,
            "address": self.address,
            "status": self.status,
            "value": self.value,
            "date_created": self.date_created
        }

    def from_dict(self, data):
        for field in ['first_name', 'last_name', 'phone_number', 'cell_phone_number', 'business_name', 'address', 'status', 'value']:
            if field in data:
                setattr(self, field, data[field])

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


# #############################################
#                  EVENT MODEL 
# #############################################

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime(), nullable=False)
    event_name = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunity.id'))

    def __init__(self, date_time=None, event_name=None, first_name=None, last_name=None, opportunity_id=None):
        self.date_time = date_time
        self.event_name = event_name
        self.first_name = first_name
        self.last_name = last_name
        self.opportunity_id = opportunity_id

    def __repr__(self):
        return f'<Event Object | {self.event_name}>'

    def __str__(self):
        return f'Event - {self.id} - {self.event_name}'

    def to_dict(self):
        return {
            "id": self.id,
            "date_time": self.date_time,
            "first_name": self.first_name,
            "last_name": self.last_name
        }

    def from_dict(self, data):
        for field in ['date_time', 'event_name', 'first_name', 'last_name', 'opportunity_id']:
            if field in data:
                setattr(self, field, data[field])

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


# #############################################
#                ACTIVITY MODEL 
# #############################################

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date(), nullable=False)
    notes = db.Column(db.String(2000), nullable=False)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'))
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunity.id'))

    def __init__(self, type=None, date=None, notes=None, lead_id=None, opportunity_id=None):
        self.type = type
        self.date = date
        self.notes = notes
        self.lead_id = lead_id
        self.opportunity_id = opportunity_id

    def __repr__(self):
        return f'<Activity Object | {self.type}>'

    def __str__(self):
        return f'Activity - {self.id} - {self.type}'

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "date": self.date,
            "notes": self.notes
        }

    def from_dict(self, data):
        for field in ['type', 'date', 'notes', 'lead_id', 'opportunity_id']:
            if field in data:
                setattr(self, field, data[field])

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()