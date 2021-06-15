from os import abort
from . import bp as api
from app import db
from flask import request, jsonify, json, abort
from datetime import date, datetime, time, timedelta
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
    recent_leads = Lead.query.filter(Lead.user_id == token_auth.current_user().id).filter(Lead.open == True).order_by(desc('date_created')).limit(5)
    recent_leads = [l.to_dict() for l in recent_leads]
    return jsonify([recent_leads])

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

# Get All Open Leads
@api.route('/allopenleads')
@token_auth.login_required
def all_open_leads():
    open_leads = Lead.query.filter(Lead.user_id == token_auth.current_user().id).filter(Lead.open == True).order_by(desc('date_created'))
    return jsonify([l.to_dict() for l in open_leads])

# Get all open leads, last 30 days
@api.route('/openleadsthismonth')
@token_auth.login_required
def this_month_open_leads():
    this_month = datetime.today() - timedelta(days=30)
    this_month_leads = Lead.query.filter(Lead.user_id == token_auth.current_user().id).filter(Lead.open == True).filter(Lead.date_created > this_month).order_by(desc('date_created'))
    return jsonify([l.to_dict() for l in this_month_leads])

# Get all open leads, hot
@api.route('/openhotleads')
@token_auth.login_required
def open_hot_leads():
    hot_leads = Lead.query.filter(Lead.user_id == token_auth.current_user().id).filter(Lead.open == True).filter(Lead.hot == True).order_by(desc('date_created'))
    return jsonify([l.to_dict() for l in hot_leads])

# Hot and fresh leads... mmmm
@api.route('/hotleadsthismonth')
@token_auth.login_required
def hot_this_month():
    this_month = datetime.today() - timedelta(days=30)
    hot_this_month = Lead.query.filter(Lead.user_id == token_auth.current_user().id).filter(Lead.open == True).filter(Lead.hot == True).filter(Lead.date_created > this_month).order_by(desc('date_created'))
    return jsonify([l.to_dict() for l in hot_this_month])

# Single Lead Detail
@api.route('/leads/<int:id>')
@token_auth.login_required
def single_lead(id):
    lead = Lead.query.get(id)
    if lead.user_id != token_auth.current_user().id:
        return abort(403)
    else:
        return jsonify(lead.to_dict())

# Edit Lead
@api.route('/edit/lead/<int:id>', methods=['POST'])
@token_auth.login_required
def edit_lead(id):
    lead = Lead.query.get(id)
    if lead.user_id != token_auth.current_user().id:
        return abort(403)
    else:
        data = request.get_json()
        lead.from_dict(data)
        lead.save()
        return jsonify(lead.to_dict())
