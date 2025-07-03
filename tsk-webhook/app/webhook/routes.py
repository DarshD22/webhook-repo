from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app.extensions import mongo

webhook = Blueprint('webhook', __name__)

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
            "timestamp": datetime.utcnow()  # Store as datetime object
        }

    elif 'pull_request' in payload:
        pr = payload['pull_request']
        action_type = "merge" if payload['action'] == "closed" and pr.get('merged') else "pull_request"

        entry = {
            "action": action_type,
            "author": pr['user']['login'],
            "from_branch": pr['head']['ref'],
            "to_branch": pr['base']['ref'],
            "timestamp": datetime.utcnow()  # Store as datetime object
        }

    else:
        return jsonify({"msg": "Unsupported event"}), 400

    mongo.db.events.insert_one(entry)
    return jsonify({"msg": "Event stored"}), 200


@webhook.route('/events', methods=['GET'])
def get_events():
    # Only fetch events from the last 20 seconds
    cutoff_time = datetime.utcnow() - timedelta(seconds=20)

    # Filter events with timestamp newer than cutoff
    events = list(mongo.db.events.find({
        "timestamp": {"$gt": cutoff_time}
    }).sort('_id', -1).limit(10))

    # Convert to response format
    for e in events:
        e['_id'] = str(e['_id'])
        # Format timestamp for display
        e['timestamp'] = e['timestamp'].strftime('%d %B %Y - %I:%M %p UTC')
    
    return jsonify(events)