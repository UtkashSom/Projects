from celery import Celery
from Code.app import app, redis_client
from models.models import Campaign

celery = Celery(app.name, broker='redis://localhost:6379/0')

@celery.task
def send_daily_reminders():
    # Example function to send daily reminders
    campaigns = Campaign.query.all()
    for campaign in campaigns:
        # Logic to send reminders
        pass
