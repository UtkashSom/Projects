from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.decorators import admin_required
from app.models import User, Subject, Chapter, Quiz, Question
from app import db

bp = Blueprint('admin', __name__)

@bp.route('/dashboard')
@jwt_required()
@admin_required()
def dashboard():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    return jsonify({
        'status': 'success',
        'message': 'Admin dashboard accessed successfully',
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'is_admin': user.is_admin
        }
    }), 200

# Subject routes
@bp.route('/subjects', methods=['GET'])
@jwt_required()
@admin_required()
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description
    } for s in subjects]), 200

@bp.route('/subjects', methods=['POST'])
@jwt_required()
@admin_required()
def create_subject():
    data = request.get_json()
    subject = Subject(
        name=data['name'],
        description=data.get('description')
    )
    db.session.add(subject)
    db.session.commit()
    return jsonify({
        'id': subject.id,
        'name': subject.name,
        'description': subject.description
    }), 201

@bp.route('/subjects/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_subject(id):
    subject = Subject.query.get_or_404(id)
    data = request.get_json()
    subject.name = data.get('name', subject.name)
    subject.description = data.get('description', subject.description)
    db.session.commit()
    return jsonify({
        'id': subject.id,
        'name': subject.name,
        'description': subject.description
    }), 200

@bp.route('/subjects/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    return '', 204

# Chapter routes
@bp.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
@jwt_required()
@admin_required()
def get_chapters(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description,
        'subject_id': c.subject_id
    } for c in chapters]), 200

@bp.route('/subjects/<int:subject_id>/chapters', methods=['POST'])
@jwt_required()
@admin_required()
def create_chapter(subject_id):
    data = request.get_json()
    chapter = Chapter(
        name=data['name'],
        description=data.get('description'),
        subject_id=subject_id
    )
    db.session.add(chapter)
    db.session.commit()
    return jsonify({
        'id': chapter.id,
        'name': chapter.name,
        'description': chapter.description,
        'subject_id': chapter.subject_id
    }), 201

@bp.route('/chapters/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    data = request.get_json()
    chapter.name = data.get('name', chapter.name)
    chapter.description = data.get('description', chapter.description)
    db.session.commit()
    return jsonify({
        'id': chapter.id,
        'name': chapter.name,
        'description': chapter.description,
        'subject_id': chapter.subject_id
    }), 200

@bp.route('/chapters/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    db.session.delete(chapter)
    db.session.commit()
    return '', 204

# Quiz routes
@bp.route('/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@jwt_required()
@admin_required()
def get_quizzes(chapter_id):
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return jsonify([{
        'id': q.id,
        'title': q.title,
        'description': q.description,
        'duration_minutes': q.duration_minutes,
        'chapter_id': q.chapter_id
    } for q in quizzes]), 200

@bp.route('/chapters/<int:chapter_id>/quizzes', methods=['POST'])
@jwt_required()
@admin_required()
def create_quiz(chapter_id):
    data = request.get_json()
    quiz = Quiz(
        title=data['title'],
        description=data.get('description'),
        duration_minutes=data.get('duration_minutes', 30),
        chapter_id=chapter_id
    )
    db.session.add(quiz)
    db.session.commit()
    return jsonify({
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'duration_minutes': quiz.duration_minutes,
        'chapter_id': quiz.chapter_id
    }), 201

@bp.route('/quizzes/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    data = request.get_json()
    quiz.title = data.get('title', quiz.title)
    quiz.description = data.get('description', quiz.description)
    quiz.duration_minutes = data.get('duration_minutes', quiz.duration_minutes)
    db.session.commit()
    return jsonify({
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'duration_minutes': quiz.duration_minutes,
        'chapter_id': quiz.chapter_id
    }), 200

@bp.route('/quizzes/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    db.session.delete(quiz)
    db.session.commit()
    return '', 204

# Question routes
@bp.route('/quizzes/<int:quiz_id>/questions', methods=['GET'])
@jwt_required()
@admin_required()
def get_questions(quiz_id):
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return jsonify([{
        'id': q.id,
        'text': q.text,
        'option_a': q.option_a,
        'option_b': q.option_b,
        'option_c': q.option_c,
        'option_d': q.option_d,
        'quiz_id': q.quiz_id
    } for q in questions]), 200

@bp.route('/quizzes/<int:quiz_id>/questions', methods=['POST'])
@jwt_required()
@admin_required()
def create_question(quiz_id):
    data = request.get_json()
    question = Question(
        text=data['text'],
        option_a=data['option_a'],
        option_b=data['option_b'],
        option_c=data['option_c'],
        option_d=data['option_d'],
        correct_answer=data['correct_answer'],
        quiz_id=quiz_id
    )
    db.session.add(question)
    db.session.commit()
    return jsonify({
        'id': question.id,
        'text': question.text,
        'option_a': question.option_a,
        'option_b': question.option_b,
        'option_c': question.option_c,
        'option_d': question.option_d,
        'quiz_id': question.quiz_id
    }), 201

@bp.route('/questions/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_question(id):
    question = Question.query.get_or_404(id)
    data = request.get_json()
    question.text = data.get('text', question.text)
    question.option_a = data.get('option_a', question.option_a)
    question.option_b = data.get('option_b', question.option_b)
    question.option_c = data.get('option_c', question.option_c)
    question.option_d = data.get('option_d', question.option_d)
    question.correct_answer = data.get('correct_answer', question.correct_answer)
    db.session.commit()
    return jsonify({
        'id': question.id,
        'text': question.text,
        'option_a': question.option_a,
        'option_b': question.option_b,
        'option_c': question.option_c,
        'option_d': question.option_d,
        'quiz_id': question.quiz_id
    }), 200

@bp.route('/questions/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_question(id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    return '', 204

# User management routes
@bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required()
def get_users():
    users = User.query.filter_by(is_admin=False).all()
    return jsonify([{
        'id': u.id,
        'email': u.email,
        'full_name': u.full_name,
        'qualification': u.qualification,
        'date_of_birth': u.date_of_birth.isoformat() if u.date_of_birth else None,
        'created_at': u.created_at.isoformat()
    } for u in users]), 200