from flask import jsonify, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Quiz, Question, QuizAttempt, QuizResult
from datetime import datetime

# User routes
class UserRegistration(Resource):
    def post(self):
        data = request.get_json()
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already registered'}, 400
        
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=data['password']  # Note: In production, hash the password
        )
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User registered successfully'}, 201

class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.id)
            return {'access_token': access_token}, 200
        return {'message': 'Invalid credentials'}, 401

# Quiz routes
class QuizList(Resource):
    @jwt_required()
    def get(self):
        quizzes = Quiz.query.all()
        return [quiz.to_dict() for quiz in quizzes]

    @jwt_required()
    def post(self):
        data = request.get_json()
        new_quiz = Quiz(
            title=data['title'],
            description=data['description'],
            creator_id=get_jwt_identity()
        )
        db.session.add(new_quiz)
        db.session.commit()
        return new_quiz.to_dict(), 201

class QuizDetail(Resource):
    @jwt_required()
    def get(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        return quiz.to_dict()

    @jwt_required()
    def put(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        if quiz.creator_id != get_jwt_identity():
            return {'message': 'Unauthorized'}, 403
        
        data = request.get_json()
        quiz.title = data.get('title', quiz.title)
        quiz.description = data.get('description', quiz.description)
        db.session.commit()
        return quiz.to_dict()

    @jwt_required()
    def delete(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        if quiz.creator_id != get_jwt_identity():
            return {'message': 'Unauthorized'}, 403
        
        db.session.delete(quiz)
        db.session.commit()
        return '', 204

# Question routes
class QuestionList(Resource):
    @jwt_required()
    def get(self, quiz_id):
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        return [question.to_dict() for question in questions]

    @jwt_required()
    def post(self, quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        if quiz.creator_id != get_jwt_identity():
            return {'message': 'Unauthorized'}, 403
        
        data = request.get_json()
        new_question = Question(
            quiz_id=quiz_id,
            question_text=data['question_text'],
            correct_answer=data['correct_answer'],
            options=data['options']
        )
        db.session.add(new_question)
        db.session.commit()
        return new_question.to_dict(), 201

# Quiz attempt routes
class QuizAttemptList(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
        return [attempt.to_dict() for attempt in attempts]

    @jwt_required()
    def post(self):
        data = request.get_json()
        new_attempt = QuizAttempt(
            user_id=get_jwt_identity(),
            quiz_id=data['quiz_id'],
            start_time=datetime.utcnow()
        )
        db.session.add(new_attempt)
        db.session.commit()
        return new_attempt.to_dict(), 201

# Register routes
api.add_resource(UserRegistration, '/api/register')
api.add_resource(UserLogin, '/api/login')
api.add_resource(QuizList, '/api/quizzes')
api.add_resource(QuizDetail, '/api/quizzes/<int:quiz_id>')
api.add_resource(QuestionList, '/api/quizzes/<int:quiz_id>/questions')
api.add_resource(QuizAttemptList, '/api/attempts') 