from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app.extensions import mongo

webhook = Blueprint('webhook', __name__)

# In-memory set to track sent event IDs (in production, consider using Redis)
sent_event_ids = set()

@webhook.route('/webhook', methods=['POST'])
def github_webhook():
    payload = request.json

    entry = {}

    if 'commits' in payload:
        entry = {
            "action": "push",
            "author": payload['pusher']['name'],
            "from_branch": None,
            "to_branch": payload['ref'].split('/')[-1],
            "timestamp": datetime.utcnow()
        }

    elif 'pull_request' in payload:
        pr = payload['pull_request']
        action_type = "merge" if payload['action'] == "closed" and pr.get('merged') else "pull_request"

        entry = {
            "action": action_type,
            "author": pr['user']['login'],
            "from_branch": pr['head']['ref'],
            "to_branch": pr['base']['ref'],
            "timestamp": datetime.utcnow()
        }

    else:
        return jsonify({"msg": "Unsupported event"}), 400

    mongo.db.events.insert_one(entry)
    return jsonify({"msg": "Event stored"}), 200


@webhook.route('/events', methods=['GET'])
def get_events():
    global sent_event_ids
    
    # Get all recent events (last 5 minutes to ensure we don't miss any)
    cutoff_time = datetime.utcnow() - timedelta(seconds=15)
    
    # Fetch events from database
    all_events = list(mongo.db.events.find({
        "timestamp": {"$gt": cutoff_time}
    }).sort('_id', -1))
    
    # Filter out events that have already been sent
    new_events = []
    for event in all_events:
        event_id = str(event['_id'])
        if event_id not in sent_event_ids:
            new_events.append(event)
            sent_event_ids.add(event_id)
    
    # Clean up old IDs from sent_event_ids to prevent memory leaks
    # Remove IDs older than 10 mins
    old_cutoff = datetime.utcnow() - timedelta(minutes=10)
    old_events = list(mongo.db.events.find({
        "timestamp": {"$lt": old_cutoff}
    }))
    
    for old_event in old_events:
        sent_event_ids.discard(str(old_event['_id']))
    
    # Format response
    for event in new_events:
        event['_id'] = str(event['_id'])
        event['timestamp'] = event['timestamp'].strftime('%d %B %Y - %I:%M %p UTC')
    
    return jsonify(new_events)


@webhook.route('/events/reset', methods=['POST'])
def reset_sent_events():
    """Optional endpoint to reset the sent events tracking (useful for testing)"""
    global sent_event_ids
    sent_event_ids.clear()
    return jsonify({"msg": "Sent events tracking reset"}), 200