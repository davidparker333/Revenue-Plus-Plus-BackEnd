from . import bp as api
from app import db
from flask import request, jsonify, abort
from datetime import date, datetime, timedelta
from app.blueprints.api.models import User, Lead, Opportunity, Activity, Event
from sqlalchemy import desc
from .auth import token_auth

# ##################################
#           Registration
# ##################################

# Register a new user
@api.route('/register', methods=['POST'])
def register():
    user = User()
    data = request.get_json()
    user.from_dict(data)
    user.save()
    return jsonify(user.to_dict())


# ##################################
#           Home Page
# ##################################

# Home Page - Display Recent info from 4 categories
@api.route('/crmhome', methods=['GET'])
@token_auth.login_required
def home():
    today = datetime.today()
    tomorrow = datetime.today() + timedelta(days=1)
    recent_leads = Lead.query.filter(Lead.user_id == token_auth.current_user().id).filter(Lead.open == True).order_by(desc('date_created')).limit(5)
    recent_leads = [l.to_dict() for l in recent_leads]
    recent_opps = Opportunity.query.filter(Opportunity.user_id == token_auth.current_user().id).filter(Opportunity.open == True).order_by(desc('date_created')).limit(5)
    recent_opps = [o.to_dict() for o in recent_opps]
    closed_opps = Opportunity.query.filter(Opportunity.user_id == token_auth.current_user().id).filter(Opportunity.open == False).filter(Opportunity.status == "Closed Won").order_by(desc('date_created')).limit(5)
    closed_opps = [co.to_dict() for co in closed_opps]
    today_events = Event.query.join(Opportunity).join(User).filter(User.id == token_auth.current_user().id).filter(Event.date_time > today).filter(Event.date_time < tomorrow).order_by('date_time').limit(5)
    today_events = [e.to_dict() for e in today_events]
    return jsonify([recent_leads, recent_opps, closed_opps, today_events])


# ##################################
#               Leads
# ##################################

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

# Delete Lead
@api.route('/delete/lead/<int:id>', methods=['POST'])
@token_auth.login_required
def delete_lead(id):
    lead = Lead.query.get(id)
    lead.open = False
    lead.status = "Closed Lost"
    lead.save()
    return jsonify({"status": "deleted"})


# ##################################
#           Lead Activities 
# ##################################

# Create Lead Activity
@api.route('/newactivity/lead/<int:id>', methods=['POST'])
@token_auth.login_required
def post_activity_lead(id):
    lead = Lead.query.get(id)
    activity = Activity()
    data = request.get_json()
    activity.from_dict(data)
    activity.lead_id = lead.id
    activity.save()
    return jsonify(activity.to_dict())

# Get Activity - Lead
@api.route('/getactivity/lead/<int:id>')
@token_auth.login_required
def get_activity_lead(id):
    lead = Lead.query.get(id)
    if lead.user_id != token_auth.current_user().id:
        return abort(403)
    activity = Activity.query.filter(Activity.lead_id == id).order_by(desc('date'))
    return jsonify([a.to_dict() for a in activity])


# ##################################
#           Lead Conversion
# ##################################
        
# Convert Lead to Opp
@api.route('/convert/<int:id>', methods=['POST'])
@token_auth.login_required
def convert_lead(id):
    lead = Lead.query.get(id)
    if lead.user_id != token_auth.current_user().id:
        return abort(403)
    lead.convert()
    opportunity = Opportunity.query.filter(Opportunity.lead_id == lead.id).first()
    meeting = Event()
    data = request.get_json()
    meeting.from_dict(data)
    meeting.opportunity_id = opportunity.id
    meeting.save()
    return jsonify([opportunity.to_dict(), meeting.to_dict()])


# ##################################
#           Opportunities
# ##################################

# Get all opportunities
@api.route('/allopenopportunities')
@token_auth.login_required
def all_open_opportunities():
    opps = Opportunity.query.filter(Opportunity.user_id == token_auth.current_user().id).filter(Opportunity.open == True).order_by(desc('date_created'))
    return jsonify([o.to_dict() for o in opps])

# Get all opportunities created less than 30 days ago
@api.route('/openopportunitiesthismonth')
@token_auth.login_required
def fresh_open_opportunities():
    this_month = datetime.today() - timedelta(days=30)
    opps = Opportunity.query.filter(Opportunity.user_id == token_auth.current_user().id).filter(Opportunity.open == True).filter(Opportunity.date_created > this_month).order_by(desc('date_created'))
    return jsonify([o.to_dict() for o in opps])

# Get a single opportunity
@api.route('/opportunities/<int:id>')
@token_auth.login_required
def single_opp(id):
    opp = Opportunity.query.get(id)
    if opp.user_id != token_auth.current_user().id:
        return abort(403)
    else:
        return jsonify(opp.to_dict())

# Edit Opportunity
@api.route('/edit/opportunity/<int:id>', methods=['POST'])
@token_auth.login_required
def edit_opportunity(id):
    opp = Opportunity.query.get(id)
    if opp.user_id != token_auth.current_user().id:
        return abort(403)
    else:
        data = request.get_json()
        opp.from_dict(data)
        opp.save()
        return jsonify(opp.to_dict())

# Close Won Opportunity
@api.route('/close/won/opportunity/<int:id>', methods=['POST'])
@token_auth.login_required
def closed_won(id):
    opp = Opportunity.query.get(id)
    if opp.user_id != token_auth.current_user().id:
        return abort(403)
    else:
        opp.open = False
        opp.status = "Closed Won"
        opp.save()
    return jsonify(opp.to_dict())

# Close Lost Opportunity
@api.route('/close/lost/opportunity/<int:id>', methods=['POST'])
@token_auth.login_required
def closed_lost(id):
    opp = Opportunity.query.get(id)
    if opp.user_id != token_auth.current_user().id:
        return abort(403)
    else:
        opp.open = False
        opp.status = "Closed Lost"
        opp.save()
    return jsonify(opp.to_dict())


# ##################################
#      Opportunitiy Activities
# ##################################

# Add Opportunity Activity
@api.route('/newactivity/opportunity/<int:id>', methods=['POST'])
@token_auth.login_required
def post_activity_opp(id):
    opp = Opportunity.query.get(id)
    activity = Activity()
    data = request.get_json()
    activity.from_dict(data)
    activity.opportunity_id = opp.id
    activity.save()
    return jsonify(activity.to_dict())

# Get Opportunity Activities
@api.route('/getactivity/opportunity/<int:id>')
@token_auth.login_required
def get_activity_opp(id):
    opp = Opportunity.query.get(id)
    if opp.user_id != token_auth.current_user().id:
        return abort(403)
    else:
        activity = Activity.query.filter(Activity.opportunity_id == id).order_by(desc('date'))
        return jsonify([a.to_dict() for a in activity])


# ##################################
#              Events
# ##################################

# Create Event on Opportunity
@api.route('/addevent/<int:id>', methods=['POST'])
@token_auth.login_required
def create_opp_event(id):
    opp = Opportunity.query.get(id)
    if opp.user_id != token_auth.current_user().id:
        return abort(403)
    else:
        event = Event()
        data = request.get_json()
        event.from_dict(data)
        event.opportunity_id = opp.id
        event.save()
        return jsonify(event.to_dict())

# Get Events
@api.route('/allevents')
@token_auth.login_required
def get_all_events():
    today = datetime.today()
    events = Event.query.join(Opportunity).join(User).filter(User.id == token_auth.current_user().id).filter(Event.date_time > today).order_by('date_time').all()
    return jsonify([e.to_dict() for e in events])

# Get Events this week
@api.route('/eventsthisweek')
@token_auth.login_required
def get_events_this_week():
    today = datetime.today()
    this_week = datetime.today() + timedelta(days=7)
    events = Event.query.join(Opportunity).join(User).filter(User.id == token_auth.current_user().id).filter(Event.date_time > today).filter(Event.date_time < this_week).order_by('date_time').all()
    return jsonify([e.to_dict() for e in events])

# Get Single Event
@api.route('/events/<int:id>')
@token_auth.login_required
def get_single_event(id):
    event = Event.query.get(id)
    if event.opportunity.user_id != token_auth.current_user().id:
        return abort(403)
    else:
        return jsonify(event.to_dict())

# Edit Event
@api.route('/edit/event/<int:id>', methods=['POST'])
@token_auth.login_required
def edit_event(id):
    event = Event.query.get(id)
    if event.opportunity.user_id != token_auth.current_user().id:
        return abort(403)
    else:
        data = request.get_json()
        event.from_dict(data)
        event.save()
        return jsonify(event.to_dict())

# Delete Event
@api.route('/delete/event/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_event(id):
    event = Event.query.get(id)
    if event.opportunity.user_id != token_auth.current_user().id:
        return abort(403)
    else:
        event.delete()
        return jsonify({"status": "deleted"})


# ##################################
#             Search
# ##################################

@api.route('/search', methods=['GET'])
@token_auth.login_required
def search():
    params = request.args.get('search')
    leads = Lead.query.filter(Lead.user_id == token_auth.current_user().id).filter(Lead.open == True).filter(Lead.business_name.match('%' + params + '%')).all()
    leads = [l.to_dict() for l in leads]
    opps = Opportunity.query.filter(Opportunity.user_id == token_auth.current_user().id).filter(Opportunity.business_name.match('%' + params + '%')).all()
    opps = [o.to_dict() for o in opps]
    return jsonify([leads, opps])


# ##################################
#             Reports
# ##################################

# All Closed Lost Leads
@api.route('/reports/closedleads')
@token_auth.login_required
def closed_leads():
    leads = Lead.query.filter(Lead.user_id == token_auth.current_user().id).filter(Lead.open == False).order_by(desc('date_created')).all()
    opps = Opportunity.query.filter(Opportunity.user_id == token_auth.current_user().id).all()
    converted_lead_ids = []
    result = []
    for opp in opps:
        converted_lead_ids.append(opp.lead_id)
    for lead in leads:
        if lead.id not in converted_lead_ids:
            result.append(lead)
    return jsonify([l.to_dict() for l in result])

# Closed Won Opps
@api.route('/reports/closedwonopportunities')
@token_auth.login_required
def closed_won_opps():
    opps = Opportunity.query.filter(Opportunity.user_id == token_auth.current_user().id).filter(Opportunity.open == False).filter(Opportunity.status == "Closed Won").order_by(desc('date_created'))
    return jsonify([o.to_dict() for o in opps])

# Closed Lost Opps
@api.route('/reports/closedlostopportunities')
@token_auth.login_required
def closed_lost_opp():
    opps = Opportunity.query.filter(Opportunity.user_id == token_auth.current_user().id).filter(Opportunity.open == False).filter(Opportunity.status == "Closed Lost").order_by(desc('date_created'))
    return jsonify([o.to_dict() for o in opps])

# High Value Opps
@api.route('/reports/highvalueopps')
@token_auth.login_required
def high_value_opps():
    params = request.args.get('value')
    opps = Opportunity.query.filter(Opportunity.user_id == token_auth.current_user().id).filter(Opportunity.value >= params).order_by(desc('date_created'))
    return jsonify([o.to_dict() for o in opps])

# Low Value Opps
@api.route('/reports/lowvalueopps')
@token_auth.login_required
def low_value_opps():
    params = request.args.get('value')
    opps = Opportunity.query.filter(Opportunity.user_id == token_auth.current_user().id).filter(Opportunity.value <= params).order_by(desc('date_created'))
    return jsonify([o.to_dict() for o in opps])

# All Converted Leads
@api.route('/reports/convertedleads')
@token_auth.login_required
def converted_leads():
    leads = Lead.query.join(Opportunity).filter(Opportunity.user_id == token_auth.current_user().id).order_by(desc('date_created'))
    return jsonify([l.to_dict() for l in leads])