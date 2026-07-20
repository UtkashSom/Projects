import pytest
from app import create_app, db
from app.models import User, Subject, Chapter, Quiz, Question
from datetime import datetime

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_token(app, client):
    # Create admin user
    admin = User(
        email='admin@test.com',
        password='admin123',
        full_name='Admin User',
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    
    # Login and get token
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    return response.json['access_token']

@pytest.fixture
def test_data(app):
    # Create test subject
    subject = Subject(name='Test Subject', description='Test Description')
    db.session.add(subject)
    db.session.commit()
    
    # Create test chapter
    chapter = Chapter(
        name='Test Chapter',
        description='Test Chapter Description',
        subject_id=subject.id
    )
    db.session.add(chapter)
    db.session.commit()
    
    # Create test quiz
    quiz = Quiz(
        title='Test Quiz',
        description='Test Quiz Description',
        duration_minutes=30,
        chapter_id=chapter.id
    )
    db.session.add(quiz)
    db.session.commit()
    
    # Create test question
    question = Question(
        text='Test Question',
        option_a='Option A',
        option_b='Option B',
        option_c='Option C',
        option_d='Option D',
        correct_answer='A',
        quiz_id=quiz.id
    )
    db.session.add(question)
    db.session.commit()
    
    return {
        'subject_id': subject.id,
        'chapter_id': chapter.id,
        'quiz_id': quiz.id,
        'question_id': question.id
    }

def test_admin_dashboard(client, admin_token):
    response = client.get('/api/admin/dashboard', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert 'user' in response.json

def test_get_subjects(client, admin_token):
    response = client.get('/api/admin/subjects', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_create_subject(client, admin_token):
    data = {'name': 'New Subject', 'description': 'New Description'}
    response = client.post('/api/admin/subjects', 
                         json=data,
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 201
    assert response.json['name'] == data['name']

def test_update_subject(client, admin_token, test_data):
    data = {'name': 'Updated Subject', 'description': 'Updated Description'}
    response = client.put(f'/api/admin/subjects/{test_data["subject_id"]}',
                        json=data,
                        headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert response.json['name'] == data['name']

def test_delete_subject(client, admin_token, test_data):
    response = client.delete(f'/api/admin/subjects/{test_data["subject_id"]}',
                           headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 204
    subject = Subject.query.get(test_data['subject_id'])
    assert subject is None

def test_get_chapters(client, admin_token, test_data):
    response = client.get(f'/api/admin/subjects/{test_data["subject_id"]}/chapters',
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_create_chapter(client, admin_token, test_data):
    data = {'name': 'New Chapter', 'description': 'New Description'}
    response = client.post(f'/api/admin/subjects/{test_data["subject_id"]}/chapters',
                         json=data,
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 201
    assert response.json['name'] == data['name']

def test_update_chapter(client, admin_token, test_data):
    data = {'name': 'Updated Chapter', 'description': 'Updated Description'}
    response = client.put(f'/api/admin/chapters/{test_data["chapter_id"]}',
                        json=data,
                        headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert response.json['name'] == data['name']

def test_delete_chapter(client, admin_token, test_data):
    response = client.delete(f'/api/admin/chapters/{test_data["chapter_id"]}',
                           headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 204
    chapter = Chapter.query.get(test_data['chapter_id'])
    assert chapter is None

def test_get_quizzes(client, admin_token, test_data):
    response = client.get(f'/api/admin/chapters/{test_data["chapter_id"]}/quizzes',
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_create_quiz(client, admin_token, test_data):
    data = {
        'title': 'New Quiz',
        'description': 'New Description',
        'duration_minutes': 45
    }
    response = client.post(f'/api/admin/chapters/{test_data["chapter_id"]}/quizzes',
                         json=data,
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 201
    assert response.json['title'] == data['title']

def test_update_quiz(client, admin_token, test_data):
    data = {
        'title': 'Updated Quiz',
        'description': 'Updated Description',
        'duration_minutes': 60
    }
    response = client.put(f'/api/admin/quizzes/{test_data["quiz_id"]}',
                        json=data,
                        headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert response.json['title'] == data['title']

def test_delete_quiz(client, admin_token, test_data):
    response = client.delete(f'/api/admin/quizzes/{test_data["quiz_id"]}',
                           headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 204
    quiz = Quiz.query.get(test_data['quiz_id'])
    assert quiz is None

def test_get_questions(client, admin_token, test_data):
    response = client.get(f'/api/admin/quizzes/{test_data["quiz_id"]}/questions',
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_create_question(client, admin_token, test_data):
    data = {
        'text': 'New Question',
        'option_a': 'New Option A',
        'option_b': 'New Option B',
        'option_c': 'New Option C',
        'option_d': 'New Option D',
        'correct_answer': 'B'
    }
    response = client.post(f'/api/admin/quizzes/{test_data["quiz_id"]}/questions',
                         json=data,
                         headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 201
    assert response.json['text'] == data['text']

def test_update_question(client, admin_token, test_data):
    data = {
        'text': 'Updated Question',
        'option_a': 'Updated Option A',
        'option_b': 'Updated Option B',
        'option_c': 'Updated Option C',
        'option_d': 'Updated Option D',
        'correct_answer': 'C'
    }
    response = client.put(f'/api/admin/questions/{test_data["question_id"]}',
                        json=data,
                        headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert response.json['text'] == data['text']

def test_delete_question(client, admin_token, test_data):
    response = client.delete(f'/api/admin/questions/{test_data["question_id"]}',
                           headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 204
    question = Question.query.get(test_data['question_id'])
    assert question is None

def test_get_users(client, admin_token):
    response = client.get('/api/admin/users', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert isinstance(response.json, list) 