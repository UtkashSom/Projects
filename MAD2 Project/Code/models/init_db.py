from Code.app import db
from models.models import User, Campaign

def init_db():
    db.create_all()

if __name__ == '__main__':
    init_db()
