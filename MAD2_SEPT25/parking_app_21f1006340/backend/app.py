import os
import logging
from datetime import timedelta

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import text

from models import Base, engine, SessionLocal


load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    app.config["REDIS_URL"] = "redis://localhost:6379/0"
    app.config.update(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "dev-secret-key"),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "jwt-secret-key"),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1),
        SQLALCHEMY_DATABASE_URI="sqlite:///vehicle_parking.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        REDIS_URL=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    )

    jwt = JWTManager(app)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )

    from routes import all_routes
    app.register_blueprint(all_routes, url_prefix="/api")
    
    from routes.user_parking import user_parking_bp
    app.register_blueprint(user_parking_bp, url_prefix="/api/user")

    #from routes.admin_analytics import admin_bp as admin_analytics_bp
    #app.register_blueprint(admin_analytics_bp, url_prefix="/api/admin")

    from routes.admin_lot import admin_bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    try:
        from celery_worker import configure_celery
        celery = configure_celery(app)
        app.celery = celery
    except Exception as e:
        logger.error(f"Celery initialization failed: {e}")
        app.celery = None

    @app.before_request
    def log_request():
        logger.info(f"Request: {request.method} {request.path}")
        logger.debug(f"Headers: {dict(request.headers)}")
        logger.debug(f"Body: {request.get_data()}")

    @app.after_request
    def after_request(response):
        logger.info(f"Response: {response.status}")
        return response

    @app.route("/health")
    def health_check():
        return jsonify(
            {
                "status": "healthy",
                "database": "connected" if check_db_connection() else "disconnected",
                "redis": "connected" if check_redis_connection() else "disconnected",
            }
        )

    def check_db_connection():
        try:
            session = SessionLocal()
            session.execute(text("SELECT 1"))
            session.close()
            return True
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            return False

    def check_redis_connection():
        try:
            import redis
            r = redis.Redis.from_url(app.config["REDIS_URL"])
            return r.ping()
        except Exception as e:
            logger.error(f"Redis connection error: {str(e)}")
            return False

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Server Error: {str(error)}")
        return jsonify({"error": "Internal Server Error"}), 500

    return app


app = create_app()


@app.route("/")
def index():
    return jsonify(
        {
            "name": "Vehicle Parking API",
            "version": "1.0.0",
            "status": "running",
        }
    )


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "true").lower() == "true",
    )
