from flask import Blueprint
from quiz_master_21f1006340 import db
from flask import render_template, redirect, flash, url_for
from quiz_master_21f1006340.models.chapter import Chapter
from quiz_master_21f1006340.models.question import Question
from quiz_master_21f1006340.models.quiz import Quiz
from quiz_master_21f1006340.models.score import Score
from quiz_master_21f1006340.models.subject import Subject
from quiz_master_21f1006340.models.user import User
from quiz_master_21f1006340.forms import SubjectForm, ChapterForm, QuestionForm, QuizForm
from flask_login import login_required,  current_user

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!", 'error')
        return redirect(url_for('home'))
    quizzes = Quiz.query.all()
    quiz_names =  [quiz.name for quiz in quizzes]
    return render_template("admin/dashboard.html", quiz_names=quiz_names)

@admin_bp.route("/admin/subject/manage_subjects")
@login_required
def manage_subjects():
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!")
        return redirect(url_for('home'))
    subjects = Subject.query.all()
    return render_template("admin/subject/manage_subjects.html", subjects=subjects)

@admin_bp.route("/admin/subject/add_subject", methods=['GET', 'POST'])
@login_required
def add_subject():
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!", 'error')
        return redirect(url_for('home'))
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject(name=form.name.data, description=form.description.data)
        db.session.add(subject)
        db.session.commit()
        flash("Subject added successfully", 'info')
        return redirect(url_for('admin.manage_subjects'))
    return render_template("admin/subject/add_subject.html", form=form)

@admin_bp.route("/admin/subject/edit_subject/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_subject(id):
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!", 'error')
        return redirect(url_for('home'))
    subject = Subject.query.get_or_404(id)
    form = SubjectForm(obj=subject)
    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data
        db.session.commit()
        flash("Subject edited successfully", 'info')
        return redirect(url_for('admin.manage_subjects'))
    return render_template("admin/subject/edit_subject.html", form=form)

@admin_bp.route("/admin/subject/delete_subject/<int:id>", methods=['POST'])
@login_required
def delete_subject(id):
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!", 'error')
        return redirect(url_for('home'))
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash("Subject Deleted", 'info')
    return redirect(url_for('admin.manage_subjects'))

@admin_bp.route("/admin/chapter/manage_chapters")
@login_required
def manage_chapters():
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!", 'error')
        return redirect(url_for('home'))
    chapters = Chapter.query.all()
    return render_template("admin/chapter/manage_chapters.html", chapters=chapters)

@admin_bp.route("/admin/chapter/add_chapter", methods=['GET', 'POST'])
@login_required
def add_chapter():
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!", 'error')
        return redirect(url_for('home'))
    form = ChapterForm()
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    if form.validate_on_submit():
        chapter = Chapter(name=form.name.data, description=form.description.data
                          , subject_id=form.subject_id.data)
        db.session.add(chapter)
        db.session.commit()
        flash("Chapter added successfully", 'info')
        return redirect(url_for('admin.manage_chapters'))
    return render_template("admin/chapter/add_chapter.html", form=form)

@admin_bp.route("/admin/chapter/edit_chapter/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_chapter(id):
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!", 'error')
        return redirect(url_for('home'))
    chapter = Chapter.query.get_or_404(id)
    form = ChapterForm(obj=chapter)
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    if form.validate_on_submit():
        chapter.name = form.name.data
        chapter.description = form.description.data
        chapter.subject_id = form.subject_id.data
        db.session.commit()
        flash("Chapter editted successfully", 'info')
        return redirect(url_for('admin.manage_chapters'))
    return render_template("admin/chapter/edit_chapter.html", form=form)

@admin_bp.route("/admin/chapter/delete_chapter/<int:id>", methods=['POST'])
@login_required
def delete_chapter(id):
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!")
        return redirect(url_for('home'))
    chapter = Chapter.query.get_or_404(id)
    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter Deleted", 'info')
    return redirect(url_for('admin.manage_chapters'))

@admin_bp.route("/admin/quiz/manage_quizzes")
@login_required
def manage_quizzes():
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!", 'error')
        return redirect(url_for('home'))
    quizzes = Quiz.query.all()
    return render_template("admin/quiz/manage_quizzes.html", quizzes=quizzes)

@admin_bp.route("/admin/quiz/add_quiz", methods=['GET', 'POST'])
@login_required
def add_quiz():
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!")
        return redirect(url_for('home'))
    form = QuizForm()
    form.chapter_id.choices = [(c.id, c.name) for c in Chapter.query.all()]
    if form.validate_on_submit():
        quiz = Quiz(name=form.name.data,
                    date_of_quiz=form.date_of_quiz.data, 
                    time_duration=int(form.time_duration.data),
                    chapter_id=form.chapter_id.data)
        db.session.add(quiz)
        db.session.commit()
        flash("Quiz added successfully", 'info')
        return redirect(url_for('admin.manage_quizzes'))
    return render_template("admin/quiz/add_quiz.html", form=form)

@admin_bp.route("/admin/quiz/edit_quiz/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_quiz(id):
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!", 'error')
        return redirect(url_for('home'))
    
    quiz = Quiz.query.get_or_404(id)
    form = QuizForm(obj=quiz)
    
    # Populate chapter choices
    form.chapter_id.choices = [(c.id, c.name) for c in Chapter.query.all()]
    
    if form.validate_on_submit():
        # Modify existing quiz object instead of creating a new one
        quiz.name = form.name.data
        quiz.date_of_quiz = form.date_of_quiz.data
        quiz.time_duration = int(form.time_duration.data)
        quiz.chapter_id = form.chapter_id.data
        
        db.session.commit()  # Save changes to database
        flash("Quiz edited successfully", 'info')
        return redirect(url_for('admin.manage_quizzes'))
    
    return render_template("admin/quiz/edit_quiz.html", form=form)


@admin_bp.route("/admin/quiz/delete_quiz/<int:id>", methods=['POST'])
@login_required
def delete_quiz(id):
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!", 'error')
        return redirect(url_for('home'))
    quiz = Quiz.query.get_or_404(id)
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz Deleted", 'info')
    return redirect(url_for('admin.manage_quizzes'))

@admin_bp.route("/admin/view_users")
@login_required
def view_users():
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!", 'error')
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template("admin/view_users.html", users=users)
 
@admin_bp.route("/admin/question/manage_quiz_questions/<int:quiz_id>")
@login_required
def manage_quiz_questions(quiz_id):
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!")
        return redirect(url_for('home'))
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    return render_template("admin/question/manage_quiz_questions.html", questions=questions, quiz=quiz)

@admin_bp.route("/admin/question/add_quiz_questions/<int:quiz_id>", methods=['GET', 'POST'])
@login_required
def add_quiz_questions(quiz_id):
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!", 'error')
        return redirect(url_for('home'))
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(
            question_statement = form.question_statement.data,
            option1 = form.option1.data,
            option2 = form.option2.data,
            option3 = form.option3.data,  
            option4 = form.option4.data,  
            correct_option = form.correct_option.data,
            quiz_id=quiz_id
        )
        db.session.add(question)
        db.session.commit()
        flash("Question Added to Quiz!", 'info')
        return redirect(url_for('admin.manage_quiz_questions', quiz_id=quiz_id))
    return render_template("admin/question/add_question.html", form=form, quiz_id=quiz_id)

@admin_bp.route("/admin/question/edit_quiz_question/<int:question_id>", methods=['GET', 'POST'])
@login_required
def edit_quiz_question(question_id):
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!", 'error')
        return redirect(url_for('home'))

    question = Question.query.get_or_404(question_id)
    form = QuestionForm(obj=question)

    if form.validate_on_submit():
        question.question_statement = form.question_statement.data
        question.option1 = form.option1.data
        question.option2 = form.option2.data
        question.option3 = form.option3.data
        question.option4 = form.option4.data
        question.correct_option = form.correct_option.data
        db.session.commit()
        flash("Question edited successfully", 'info')
        return redirect(url_for('admin.manage_quiz_questions', quiz_id=question.quiz_id))

    return render_template("admin/question/edit_question.html", form=form, question=question)

@admin_bp.route("/admin/question/delete_quiz_question/<int:question_id>", methods=['POST'])
@login_required
def delete_quiz_question(question_id):
    if current_user.username != "admin@iitm.ac.in":
        flash("Access Denied!", 'error')
        return redirect(url_for('home'))

    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash("Question Deleted", 'info')

    return redirect(url_for('admin.manage_quiz_questions', quiz_id=quiz_id))

@admin_bp.route('/admin/view_scores', methods=['GET'])
def view_scores():
    scores = (
    db.session.query(Score, User, Quiz)
    .join(User, Score.user_id == User.id)
    .join(Quiz, Score.quiz_id == Quiz.id)  # ✅ Ensure Quiz is joined
    .all()
)
    return render_template("/admin/view_scores.html", scores=scores)