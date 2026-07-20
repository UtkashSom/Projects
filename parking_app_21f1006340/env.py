class Config:
    SECRET_KEY = 'vault'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///parking_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'vault-token'
