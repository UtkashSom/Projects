from flask import Blueprint

bp = Blueprint('quiz', __name__)

@bp.route('/quiz/list')
def list_quizzes():
    return {'message': 'Quiz list endpoint'} 