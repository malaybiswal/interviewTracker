from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'  # This ensures the table is named 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    job_title = db.Column(db.String(120), nullable=False)
    job_url = db.Column(db.String(255))
    recruiter_name = db.Column(db.String(120))
    overall_status = db.Column(db.String(50), nullable=False, default='Applied')  # Overall interview process status
    comments = db.Column(db.Text)  # Keep for backward compatibility
    interviewer_name = db.Column(db.String(120))  # Keep for backward compatibility
    interview_date = db.Column(db.DateTime)  # Keep for backward compatibility
    interview_type = db.Column(db.String(100))  # Keep for backward compatibility
    custom_interview_type = db.Column(db.String(100))  # Keep for backward compatibility
    notes = db.Column(db.Text)  # Keep for backward compatibility
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    rounds = db.relationship('InterviewRound', backref='interview', lazy=True, cascade='all, delete-orphan')
    phone_screens = db.relationship('PhoneScreen', backref='interview', lazy=True)
    onsites = db.relationship('OnsiteInterview', backref='interview', lazy=True)

class InterviewRound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    interviewer_name = db.Column(db.String(120))
    interview_date = db.Column(db.DateTime)
    interview_type = db.Column(db.String(100))
    custom_interview_type = db.Column(db.String(100))
    status = db.Column(db.String(50), nullable=False, default='Scheduled')
    comments = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PhoneScreen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    phone_screen_date = db.Column(db.DateTime, nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    interviewer_id = db.Column(db.Integer, db.ForeignKey('interviewer.id'))  # Link to Interviewer


class OnsiteInterview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    onsite_date = db.Column(db.DateTime, nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    interviewer_id = db.Column(db.Integer, db.ForeignKey('interviewer.id'))  # Link to Interviewer


class Interviewer(db.Model):
    __tablename__ = 'interviewer'
    __table_args__ = (db.UniqueConstraint('name', 'company', name='unique_interviewer'),)
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=False)
    average_difficulty = db.Column(db.Float, default=0.0)  # Average rating (1-5)
    total_reviews = db.Column(db.Integer, default=0)  # How many times rated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ratings = db.relationship('InterviewerRating', backref='interviewer', lazy=True)

class InterviewerRating(db.Model):
    __tablename__ = 'interviewer_rating'
    __table_args__ = (db.UniqueConstraint('interviewer_id', 'user_id', name='unique_user_rating'),)
    
    id = db.Column(db.Integer, primary_key=True)
    interviewer_id = db.Column(db.Integer, db.ForeignKey('interviewer.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 scale
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
