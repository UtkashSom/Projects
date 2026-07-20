from quiz_master_21f1006340 import db

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    chapters = db.relationship('Chapter', backref='subject', lazy=True)