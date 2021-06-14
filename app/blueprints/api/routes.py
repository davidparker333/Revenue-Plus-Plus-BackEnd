from . import bp as api
from app import db
from flask import request, jsonify, json
from datetime import date, datetime, timedelta
from flask_login import current_user
from app.blueprints.api.models import User, Lead, Opportunity, Activity, Event
from sqlalchemy import desc

# Register a new user
@api.route('/register', methods=['POST'])
def register():
    user = User()
    data = request.get_json()
    user.from_dict(data)
    user.save()
    return jsonify(user.to_dict())
