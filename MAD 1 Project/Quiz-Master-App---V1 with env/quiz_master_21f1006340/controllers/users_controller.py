from flask import Blueprint
from quiz_master_21f1006340 import  db
from flask import render_template, redirect, flash, url_for, request, session
from quiz_master_21f1006340.models.chapter import Chapter
from quiz_master_21f1006340.models.quiz import Quiz
from quiz_master_21f1006340.models.score import Score
from quiz_master_21f1006340.models.subject import Subject
from flask_login import login_required, current_user
from datetime import datetime
from quiz_master_21f1006340.seed import seed_database

users_bp = Blueprint("users", __name__)

@users_bp.route("/dashboard")
@login_required
def dashboard():
    # Fetch past quiz scores for the logged-in user
    scores = Score.query.filter_by(user_id=current_user.id).all()
    total_attempted_quizzes = len(scores)
    
    # Calculate the average score for the logged-in user
    average_score = sum([s.total_scored for s in scores]) / total_attempted_quizzes if total_attempted_quizzes > 0 else 0

    # Fetch Quiz Summary Report with both user-specific and overall stats
    quiz_summary = db.session.query(
        Quiz.name.label("quiz_name"),
        db.func.count(Score.id).filter(Score.user_id == current_user.id).label("user_total_attempts"),
        db.func.avg(Score.total_scored).filter(Score.user_id == current_user.id).label("user_avg_score"),
        db.func.sum(Score.total_scored).filter(Score.user_id == current_user.id).label("user_total_score"),
        db.func.avg(Score.total_scored).label("overall_avg_score")  # Average score across all users
    ).join(Score).group_by(Quiz.id).all()

    # Convert to dictionary format for the template
    quiz_summary_list = [
        {
            "name": q.quiz_name,
            "user_total_attempts": q.user_total_attempts or 0,
            "user_avg_score": round(q.user_avg_score, 2) if q.user_avg_score else 0,
            "user_total_score": q.user_total_score or 0,
            "overall_avg_score": round(q.overall_avg_score, 2) if q.overall_avg_score else 0
        }
        for q in quiz_summary
    ]

    return render_template("user/dashboard.html",
                           scores=scores,
                           total_attempted_quizzes=total_attempted_quizzes,
                           average_score=average_score,
                           quiz_summary=quiz_summary_list)



@users_bp.route("/attempt_quiz/<int:quiz_id>", methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions

    if request.method == 'POST':
        score = 0
        feedback = []  # Store feedback for each question

        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            correct = int(user_answer) == question.correct_option if user_answer else False
            if correct:
                score += 1
            
            # Store question feedback
            feedback.append({
                "question_statement": question.question_statement,
                "user_answer": int(user_answer) if user_answer else None,
                "correct_answer": question.correct_option,
                "option1": question.option1,
                "option2": question.option2,
                "option3": question.option3,
                "option4": question.option4,
                "is_correct": correct
            })

        # Store feedback in session
        session["feedback"] = feedback

        # Save score
        user_score = Score(
            user_id=current_user.id,
            quiz_id=quiz_id,
            total_scored=score,
            timestamp=datetime.utcnow()
        )
        db.session.add(user_score)
        db.session.commit()

        flash(f'Marks Scored: {score} / {len(questions)}', 'info')
        return redirect(url_for("users.quiz_results", quiz_id=quiz_id))

    return render_template("user/attempt_quiz.html", quiz=quiz, questions=questions)


@users_bp.route("/quiz_results/int/<int:quiz_id>")
@login_required
def quiz_results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).order_by(Score.timestamp.desc()).first()
    
    feedback = session.pop('feedback', [])  # Retrieve feedback from session

    return render_template("user/quiz_results.html", quiz=quiz, score=score, feedback=feedback)

@users_bp.route("/select-quiz", methods=['GET', 'POST'])
@login_required
def select_quiz():
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quizzes = Quiz.query.all()

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        chapter_id = request.form.get('chapter_id')

        if subject_id:
            quizzes = Quiz.query.join(Chapter).filter(Chapter.subject_id == subject_id).all()
        if chapter_id:
            quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()

    return render_template("user/select-quiz.html",
                           subjects=subjects,
                           chapters=chapters,
                           quizzes=quizzes)