from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    job_title = db.Column(db.String(120), nullable=False)
    job_url = db.Column(db.String(255))
    recruiter_name = db.Column(db.String(120))
    status = db.Column(db.String(50), nullable=False, default='Applied')
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    phone_screens = db.relationship('PhoneScreen', backref='interview', lazy=True)
    onsites = db.relationship('OnsiteInterview', backref='interview', lazy=True)


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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=False)
    difficulty_rating = db.Column(db.Float, default=0)  # Average rating (1-5)
    total_reviews = db.Column(db.Integer, default=0)  # How many times rated
    comments = db.relationship('InterviewerComment', backref='interviewer', lazy=True)

class InterviewerComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interviewer_id = db.Column(db.Integer, db.ForeignKey('interviewer.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 scale
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
