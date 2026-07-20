from app import db

from .user import User
from .subject import Subject
from .chapter import Chapter
from .quiz import Quiz
from .question import Question
from .score import Score

__all__ = ['User', 'Subject', 'Chapter', 'Quiz', 'Question', 'Score'] 