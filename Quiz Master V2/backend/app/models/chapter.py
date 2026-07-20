from app import db
from datetime import datetime

class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Chapter {self.name}>' 