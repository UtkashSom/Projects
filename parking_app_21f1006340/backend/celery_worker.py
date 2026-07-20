import os
from datetime import timedelta
from celery import Celery
from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "parking_app",
    broker=redis_url,
    backend=redis_url,
    include=["tasks"],
)

celery.conf.update(
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    timezone="Asia/Dubai",
)


celery.conf.beat_schedule = {
    "send-daily-reminders-evening": {
        "task": "tasks.send_daily_reminders",
        "schedule": crontab(hour=14, minute=00),
    },
    "check-reservations-every-5-minutes": {
        "task": "tasks.check_reservations",
        "schedule": 300.0,
    },
    "send-monthly-reports-first-day": {
        "task": "tasks.send_monthly_reports",
        "schedule": crontab(day_of_month=23, hour=12, minute=30),
    },
}



def configure_celery(app):
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
