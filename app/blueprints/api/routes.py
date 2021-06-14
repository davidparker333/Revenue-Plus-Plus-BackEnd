from os import abort
from . import bp as api
from app import db
from flask import request, jsonify, json, abort
from datetime import date, datetime, timedelta
from flask_login import current_user
from app.blueprints.api.models import User, Lead, Opportunity, Activity, Event
from sqlalchemy import desc
from .auth import token_auth

# Register a new user
@api.route('/register', methods=['POST'])
def register():
    user = User()
    data = request.get_json()
    user.from_dict(data)
    user.save()
    return jsonify(user.to_dict())

# Home Page - Display Recent info from 4 categories
@api.route('/crmhome', methods=['GET'])
@token_auth.login_required
def home():
    pass

# Create Lead
@api.route('/newlead', methods=['POST'])
@token_auth.login_required
def new_lead():
    lead = Lead()
    data = request.get_json()
    lead.from_dict(data)
    lead.user_id = token_auth.current_user().id
    lead.save()
    return jsonify(lead.to_dict())