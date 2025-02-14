from flask import Blueprint, request, jsonify
from models import db, Interview, PhoneScreen, OnsiteInterview
from datetime import datetime

routes = Blueprint('routes', __name__)

@app.route('/interview', methods=['POST'])
@jwt_required()
def add_interview():
    data = request.json
    new_interview = Interview(
        user_id=get_jwt_identity(),
        company_name=data['company_name'],
        job_title=data['job_title'],
        recruiter_name=data.get('recruiter_name'),
        job_url=data.get('job_url'),
        status="Applied"
    )
    db.session.add(new_interview)
    db.session.commit()
    return jsonify({"message": "Interview added successfully"}), 201


@app.route('/interviewer', methods=['POST'])
@jwt_required()
def add_interviewer():
    data = request.json
    existing_interviewer = Interviewer.query.filter_by(name=data['name'], company=data['company']).first()
    
    if existing_interviewer:
        return jsonify({"message": "Interviewer already exists"}), 400

    new_interviewer = Interviewer(name=data['name'], company=data['company'])
    db.session.add(new_interviewer)
    db.session.commit()
    return jsonify({"message": "Interviewer added"}), 201

@app.route('/interviewer/<int:id>/rate', methods=['POST'])
@jwt_required()
def rate_interviewer(id):
    data = request.json
    interviewer = Interviewer.query.get_or_404(id)
    
    # Update rating
    new_rating = data['rating']
    interviewer.total_reviews += 1
    interviewer.difficulty_rating = ((interviewer.difficulty_rating * (interviewer.total_reviews - 1)) + new_rating) / interviewer.total_reviews

    # Add comment
    new_comment = InterviewerComment(
        interviewer_id=id,
        user_id=get_jwt_identity(),
        rating=new_rating,
        comment=data.get('comment')
    )

    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify({"message": "Rating added"}), 201

@app.route('/interviewers', methods=['GET'])
@jwt_required()
def get_interviewers():
    interviewers = Interviewer.query.all()
    result = []
    
    for i in interviewers:
        result.append({
            "id": i.id,
            "name": i.name,
            "company": i.company,
            "difficulty_rating": round(i.difficulty_rating, 2),
            "total_reviews": i.total_reviews
        })
    
    return jsonify(result)
