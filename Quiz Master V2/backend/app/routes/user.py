from flask import Blueprint

bp = Blueprint('user', __name__)

@bp.route('/user/dashboard')
def dashboard():
    return {'message': 'User dashboard endpoint'} 