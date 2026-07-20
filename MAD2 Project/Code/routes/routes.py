from flask import jsonify, request
from Code.app import app, db
from models.models import User, Campaign

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'username': user.username, 'role': user.role} for user in users])

@app.route('/campaigns', methods=['GET'])
def get_campaigns():
    campaigns = Campaign.query.all()
    return jsonify([{'id': campaign.id, 'name': campaign.name, 'description': campaign.description, 'start_date': campaign.start_date.strftime('%Y-%m-%d'), 'end_date': campaign.end_date.strftime('%Y-%m-%d'), 'budget': campaign.budget, 'visibility': campaign.visibility} for campaign in campaigns])

@app.route('/campaigns', methods=['POST'])
def create_campaign():
    data = request.json
    new_campaign = Campaign(
        name=data['name'],
        description=data['description'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        budget=data['budget'],
        visibility=data['visibility']
    )
    db.session.add(new_campaign)
    db.session.commit()
    return jsonify({'id': new_campaign.id}), 201
