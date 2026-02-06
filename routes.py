from flask import Blueprint, request, jsonify, render_template
from models import db, Interview, InterviewRound, PhoneScreen, OnsiteInterview, Interviewer, InterviewerRating, User
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token


routes = Blueprint('routes', __name__)

@routes.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Interview Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "GET /signup": "Signup page (HTML)",
            "GET /login": "Login page (HTML)",
            "GET /dashboard": "Dashboard page (HTML)",
            "GET /interview-details": "Interview details page (HTML)",
            "POST /api/signup": "Create a new user account",
            "POST /api/login": "Login and get access token",
            "GET /api/interviews": "Get user's interviews (requires auth)",
            "POST /api/interview": "Add a new interview (requires auth)",
            "PUT /api/interviews/<id>": "Update an interview (requires auth)",
            "GET /interviewers": "Get all interviewers",
            "POST /interviewer": "Add a new interviewer (requires auth)",
            "GET /interviewer/<id>/rate": "Rate an interviewer (requires auth)"
        },
        "status": "running"
    }), 200

@routes.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@routes.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@routes.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

@routes.route('/interview-details', methods=['GET'])
def interview_details():
    return render_template('interviewDetails.html')

@routes.route('/interview-rounds', methods=['GET'])
def interview_rounds():
    return render_template('interviewRounds.html')

@routes.route('/interview-table', methods=['GET'])
def interview_table():
    return render_template('interviewTable.html')

@routes.route('/interviewers', methods=['GET'])
def interviewers_page():
    return render_template('interviewers.html')

@routes.route('/interviewer-detail', methods=['GET'])
def interviewer_detail_page():
    return render_template('interviewer-detail.html')

@routes.route('/api/interview', methods=['POST'])
@jwt_required()
def add_interview():
    try:
        data = request.json
        user_id = int(get_jwt_identity())  # Convert string back to int
        
        print(f"Creating interview for user {user_id} with data: {data}")  # Debug log
        
        # Parse interview date if provided
        interview_date = None
        if data.get('interview_date') and data.get('interview_time'):
            try:
                date_str = f"{data['interview_date']} {data['interview_time']}"
                interview_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            except ValueError as ve:
                print(f"Date parsing error: {ve}")
        elif data.get('interview_datetime'):
            try:
                interview_date = datetime.fromisoformat(data['interview_datetime'].replace('T', ' '))
            except ValueError as ve:
                print(f"DateTime parsing error: {ve}")
        
        # Create interview with all fields
        new_interview = Interview(
            user_id=user_id,
            company_name=data.get('company_name', ''),
            job_title=data.get('job_title', ''),
            recruiter_name=data.get('recruiter_name'),
            interviewer_name=data.get('interviewer_name'),
            job_url=data.get('job_url'),
            interview_date=interview_date,
            interview_type=data.get('interview_type'),
            custom_interview_type=data.get('custom_interview_type'),
            overall_status=data.get('status', 'Applied'),
            comments=data.get('comments'),
            notes=data.get('notes')
        )
        
        print(f"Created interview object: {new_interview}")  # Debug log
        
        db.session.add(new_interview)
        db.session.commit()
        
        print(f"Successfully saved interview with ID: {new_interview.id}")  # Debug log
        
        return jsonify({"message": "Interview added successfully", "id": new_interview.id}), 201
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error saving interview: {str(e)}"
        print(error_msg)  # Debug log
        return jsonify({"message": error_msg}), 500

@routes.route('/api/interviews', methods=['GET'])
@jwt_required()
def get_interviews():
    user_id = int(get_jwt_identity())
    interviews = Interview.query.filter_by(user_id=user_id).all()
    
    now = datetime.utcnow()
    result = []
    
    for interview in interviews:
        # Auto-detect overall status based on rounds and dates
        actual_status = interview.overall_status
        
        # Get all rounds for this interview
        rounds = InterviewRound.query.filter_by(interview_id=interview.id).order_by(InterviewRound.round_number).all()
        
        # Calculate the most relevant date to display
        # Priority: Next upcoming date, or most recent past date
        all_dates = []
        if interview.interview_date:
            all_dates.append(interview.interview_date)
        for r in rounds:
            if r.interview_date:
                all_dates.append(r.interview_date)
        
        display_date = None
        if all_dates:
            # Get future dates
            future_dates = [d for d in all_dates if d > now]
            # Get past dates
            past_dates = [d for d in all_dates if d <= now]
            
            if future_dates:
                # Show the earliest future date (next interview)
                display_date = min(future_dates)
            elif past_dates:
                # Show the most recent past date (last interview)
                display_date = max(past_dates)
        
        # Check if any round failed - if so, overall status is Rejected
        has_failed_round = any(r.status == 'Failed' for r in rounds)
        
        if has_failed_round:
            actual_status = 'Rejected'
        # Only auto-calculate if status is not manually set to final states
        elif actual_status not in ['Offer Received', 'Rejected', 'Withdrawn', 'On Hold']:
            # Check if there are any future interviews (initial or rounds)
            has_future_initial = interview.interview_date and interview.interview_date > now
            has_future_rounds = any(r.interview_date and r.interview_date > now for r in rounds)
            
            # Check if there are any past interviews
            has_past_initial = interview.interview_date and interview.interview_date < now
            has_past_rounds = any((r.interview_date and r.interview_date < now) or r.status == 'Completed' for r in rounds)
            
            if has_future_initial or has_future_rounds:
                # Has at least one future interview/round - actively interviewing
                actual_status = 'Interviewing'
            elif (has_past_initial or has_past_rounds) and not (has_future_initial or has_future_rounds):
                # All interviews are in the past, none in future
                # Mark as "Awaiting Decision" to indicate interviews done but outcome pending
                actual_status = 'Awaiting Decision'
            elif rounds or interview.interview_date:
                # Has rounds or date but no dates set
                actual_status = 'Interviewing'
            else:
                # No rounds, no dates - just applied
                actual_status = 'Applied'
        
        result.append({
            "id": interview.id,
            "company_name": interview.company_name,
            "job_title": interview.job_title,
            "recruiter_name": interview.recruiter_name,
            "interviewer_name": interview.interviewer_name,
            "job_url": interview.job_url,
            "interview_date": display_date.isoformat() if display_date else None,
            "interview_type": interview.interview_type,
            "custom_interview_type": interview.custom_interview_type,
            "status": actual_status,
            "comments": interview.comments,
            "notes": interview.notes,
            "created_at": interview.created_at.isoformat()
        })
    
    return jsonify(result), 200

@routes.route('/api/interviews/<int:interview_id>', methods=['GET'])
@jwt_required()
def get_interview(interview_id):
    user_id = int(get_jwt_identity())
    interview = Interview.query.filter_by(id=interview_id, user_id=user_id).first()
    
    if not interview:
        return jsonify({"message": "Interview not found"}), 404
    
    # Format interview date for form inputs
    interview_date = None
    interview_time = None
    if interview.interview_date:
        interview_date = interview.interview_date.strftime('%Y-%m-%d')
        interview_time = interview.interview_date.strftime('%H:%M')
    
    # Auto-detect overall status based on rounds
    actual_status = interview.overall_status
    now = datetime.utcnow()
    
    # Get all rounds for this interview
    rounds = InterviewRound.query.filter_by(interview_id=interview_id).order_by(InterviewRound.round_number).all()
    
    # Only auto-calculate if status is not manually set to final states
    if actual_status not in ['Offer Received', 'Rejected', 'Withdrawn', 'On Hold']:
        if rounds:
            # Check if any round is completed
            has_completed_rounds = any(r.status == 'Completed' or (r.interview_date and r.interview_date < now) for r in rounds)
            # Check if all rounds are completed
            all_completed = all(r.status == 'Completed' or (r.interview_date and r.interview_date < now) for r in rounds)
            
            if has_completed_rounds:
                actual_status = 'Interviewing'
        elif interview.interview_date:
            # If initial interview has a date
            if interview.interview_date < now:
                actual_status = 'Interviewing'
    
    result = {
        "id": interview.id,
        "company_name": interview.company_name,
        "job_title": interview.job_title,
        "recruiter_name": interview.recruiter_name,
        "interviewer_name": interview.interviewer_name,
        "job_url": interview.job_url,
        "interview_date": interview_date,
        "interview_time": interview_time,
        "interview_type": interview.interview_type,
        "custom_interview_type": interview.custom_interview_type,
        "status": actual_status,
        "comments": interview.comments,
        "notes": interview.notes,
        "created_at": interview.created_at.isoformat()
    }
    
    return jsonify(result), 200

@routes.route('/api/test', methods=['GET'])
@jwt_required()
def test_auth():
    user_id = int(get_jwt_identity())
    return jsonify({"message": "Auth working", "user_id": user_id}), 200

@routes.route('/api/interviews/<int:interview_id>', methods=['PUT'])
@jwt_required()
def update_interview(interview_id):
    user_id = int(get_jwt_identity())
    interview = Interview.query.filter_by(id=interview_id, user_id=user_id).first()
    
    if not interview:
        return jsonify({"message": "Interview not found"}), 404
    
    data = request.json
    
    # Parse interview date if provided
    if data.get('interview_date') and data.get('interview_time'):
        try:
            date_str = f"{data['interview_date']} {data['interview_time']}"
            interview.interview_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
        except ValueError:
            pass
    elif data.get('interview_datetime'):
        try:
            interview.interview_date = datetime.fromisoformat(data['interview_datetime'].replace('T', ' '))
        except ValueError:
            pass
    
    # Update fields
    interview.company_name = data.get('company_name', interview.company_name)
    interview.job_title = data.get('job_title', interview.job_title)
    interview.recruiter_name = data.get('recruiter_name', interview.recruiter_name)
    interview.interviewer_name = data.get('interviewer_name', interview.interviewer_name)
    interview.job_url = data.get('job_url', interview.job_url)
    interview.interview_type = data.get('interview_type', interview.interview_type)
    interview.custom_interview_type = data.get('custom_interview_type', interview.custom_interview_type)
    interview.overall_status = data.get('status', interview.overall_status)
    interview.comments = data.get('comments', interview.comments)
    interview.notes = data.get('notes', interview.notes)
    
    try:
        db.session.commit()
        return jsonify({"message": "Interview updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error updating interview: {str(e)}"}), 500

@routes.route('/api/interviews/<int:interview_id>/rounds', methods=['GET'])
@jwt_required()
def get_interview_rounds(interview_id):
    user_id = int(get_jwt_identity())
    
    # Verify interview belongs to user
    interview = Interview.query.filter_by(id=interview_id, user_id=user_id).first()
    if not interview:
        return jsonify({"message": "Interview not found"}), 404
    
    rounds = InterviewRound.query.filter_by(interview_id=interview_id).order_by(InterviewRound.round_number).all()
    
    # Auto-detect status based on dates and logic
    now = datetime.utcnow()
    result = []
    
    for i, round in enumerate(rounds):
        # Determine the actual status
        actual_status = round.status
        
        # Only auto-detect if not in final states
        if actual_status not in ['Completed', 'Cancelled', 'No Show']:
            # Logic 1: If scheduled date is in the past, mark as Completed
            if round.interview_date and round.interview_date < now:
                actual_status = 'Completed'
            
            # Logic 2: If no scheduled date but later rounds exist and are completed
            elif not round.interview_date:
                # Check if there are any later rounds
                later_rounds = [r for r in rounds if r.round_number > round.round_number]
                if later_rounds:
                    # Check if any later round has a date or is completed
                    has_later_activity = any(
                        r.interview_date or r.status in ['Completed', 'Scheduled']
                        for r in later_rounds
                    )
                    if has_later_activity:
                        actual_status = 'Completed'
        
        result.append({
            "id": round.id,
            "round_number": round.round_number,
            "interviewer_name": round.interviewer_name,
            "interview_date": round.interview_date.isoformat() if round.interview_date else None,
            "interview_type": round.interview_type,
            "custom_interview_type": round.custom_interview_type,
            "status": actual_status,
            "comments": round.comments,
            "notes": round.notes,
            "created_at": round.created_at.isoformat()
        })
    
    return jsonify(result), 200

@routes.route('/api/interviews/<int:interview_id>/rounds', methods=['POST'])
@jwt_required()
def add_interview_rounds(interview_id):
    user_id = int(get_jwt_identity())
    
    # Verify interview belongs to user
    interview = Interview.query.filter_by(id=interview_id, user_id=user_id).first()
    if not interview:
        return jsonify({"message": "Interview not found"}), 404
    
    data = request.json
    rounds_data = data.get('rounds', [])
    
    if not rounds_data:
        return jsonify({"message": "No rounds data provided"}), 400
    
    try:
        created_rounds = []
        
        for round_data in rounds_data:
            # Parse interview date if provided
            interview_date = None
            if round_data.get('interview_date'):
                try:
                    interview_date = datetime.fromisoformat(round_data['interview_date'].replace('T', ' '))
                except ValueError:
                    pass
            
            new_round = InterviewRound(
                interview_id=interview_id,
                round_number=round_data.get('round_number'),
                interviewer_name=round_data.get('interviewer_name'),
                interview_date=interview_date,
                interview_type=round_data.get('interview_type'),
                custom_interview_type=round_data.get('custom_interview_type'),
                status=round_data.get('status', 'Scheduled'),
                comments=round_data.get('comments'),
                notes=round_data.get('notes')
            )
            
            db.session.add(new_round)
            created_rounds.append(new_round)
        
        db.session.commit()
        
        return jsonify({
            "message": f"Successfully added {len(created_rounds)} rounds",
            "rounds_added": len(created_rounds)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error adding rounds: {str(e)}"}), 500

@routes.route('/api/fix-round-numbers', methods=['POST'])
@jwt_required()
def fix_round_numbers():
    """Fix round numbers by incrementing all existing rounds by 1"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get all rounds for user's interviews, ordered by round_number descending
        rounds = db.session.query(InterviewRound).join(Interview).filter(
            Interview.user_id == user_id
        ).order_by(InterviewRound.interview_id, InterviewRound.round_number.desc()).all()
        
        updated_count = 0
        for round in rounds:
            round.round_number = round.round_number + 1
            updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            "message": f"Successfully updated {updated_count} rounds",
            "updated_count": updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error fixing round numbers: {str(e)}"}), 500

@routes.route('/api/interviewers', methods=['POST'])
@jwt_required()
def add_interviewer():
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('name') or not data.get('company'):
            return jsonify({"message": "Name and company are required"}), 400
        
        # Check for duplicate
        existing_interviewer = Interviewer.query.filter_by(
            name=data['name'], 
            company=data['company']
        ).first()
        
        if existing_interviewer:
            return jsonify({
                "message": "Interviewer already exists",
                "id": existing_interviewer.id
            }), 409

        new_interviewer = Interviewer(
            name=data['name'], 
            company=data['company']
        )
        db.session.add(new_interviewer)
        db.session.commit()
        
        return jsonify({
            "message": "Interviewer added successfully",
            "id": new_interviewer.id,
            "name": new_interviewer.name,
            "company": new_interviewer.company
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error adding interviewer: {str(e)}"}), 500

@routes.route('/api/interviewers/import-from-interviews', methods=['POST'])
@jwt_required()
def import_interviewers_from_interviews():
    """Bulk import interviewers from existing interview and interview_round data"""
    try:
        # Get unique interviewer names from interview_round table
        round_names = db.session.query(
            InterviewRound.interviewer_name,
            Interview.company_name
        ).join(Interview).filter(
            InterviewRound.interviewer_name.isnot(None),
            InterviewRound.interviewer_name != ''
        ).distinct().all()
        
        # Get unique interviewer names from interview table
        interview_names = db.session.query(
            Interview.interviewer_name,
            Interview.company_name
        ).filter(
            Interview.interviewer_name.isnot(None),
            Interview.interviewer_name != ''
        ).distinct().all()
        
        # Combine and deduplicate
        all_names = set()
        for name, company in round_names + interview_names:
            if name and company:
                all_names.add((name, company))
        
        # Import each unique combination
        imported_count = 0
        skipped_count = 0
        
        for name, company in all_names:
            # Check if already exists
            existing = Interviewer.query.filter_by(name=name, company=company).first()
            if not existing:
                new_interviewer = Interviewer(name=name, company=company)
                db.session.add(new_interviewer)
                imported_count += 1
            else:
                skipped_count += 1
        
        db.session.commit()
        
        return jsonify({
            "message": "Import completed successfully",
            "imported": imported_count,
            "skipped": skipped_count,
            "total": imported_count + skipped_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error importing interviewers: {str(e)}"}), 500

@routes.route('/api/interviewers/<int:interviewer_id>/ratings', methods=['POST'])
@jwt_required()
def rate_interviewer(interviewer_id):
    try:
        data = request.json
        user_id = int(get_jwt_identity())
        
        # Validate interviewer exists
        interviewer = Interviewer.query.get(interviewer_id)
        if not interviewer:
            return jsonify({"message": "Interviewer not found"}), 404
        
        # Validate rating value
        rating_value = data.get('rating')
        if not rating_value or not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5:
            return jsonify({"message": "Rating must be an integer between 1 and 5"}), 400
        
        # Check for duplicate rating
        existing_rating = InterviewerRating.query.filter_by(
            interviewer_id=interviewer_id,
            user_id=user_id
        ).first()
        
        if existing_rating:
            return jsonify({"message": "You have already rated this interviewer"}), 409
        
        # Create new rating
        new_rating = InterviewerRating(
            interviewer_id=interviewer_id,
            user_id=user_id,
            rating=rating_value,
            comments=data.get('comments')
        )
        
        # Update interviewer stats
        interviewer.total_reviews += 1
        interviewer.average_difficulty = (
            (interviewer.average_difficulty * (interviewer.total_reviews - 1)) + rating_value
        ) / interviewer.total_reviews
        
        db.session.add(new_rating)
        db.session.commit()
        
        return jsonify({
            "message": "Rating submitted successfully",
            "average_difficulty": round(interviewer.average_difficulty, 2),
            "total_reviews": interviewer.total_reviews
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error submitting rating: {str(e)}"}), 500

@routes.route('/api/interviewers/<int:interviewer_id>/user-rating', methods=['GET'])
@jwt_required()
def get_user_rating(interviewer_id):
    try:
        user_id = int(get_jwt_identity())
        
        # Check if user has rated this interviewer
        rating = InterviewerRating.query.filter_by(
            interviewer_id=interviewer_id,
            user_id=user_id
        ).first()
        
        if not rating:
            return jsonify({"message": "No rating found"}), 404
        
        return jsonify({
            "id": rating.id,
            "rating": rating.rating,
            "comments": rating.comments,
            "created_at": rating.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error fetching rating: {str(e)}"}), 500

@routes.route('/api/interviewers', methods=['GET'])
def get_interviewers():
    try:
        # Get search query parameter
        search = request.args.get('search', '').strip()
        include_suggestions = request.args.get('include_suggestions', 'false').lower() == 'true'
        
        # Base query
        query = Interviewer.query
        
        # Apply search filter if provided
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Interviewer.name.ilike(search_filter),
                    Interviewer.company.ilike(search_filter)
                )
            )
        
        # Sort by average_difficulty descending (hardest first)
        interviewers = query.order_by(Interviewer.average_difficulty.desc()).all()
        
        result = []
        for i in interviewers:
            result.append({
                "id": i.id,
                "name": i.name,
                "company": i.company,
                "average_difficulty": round(i.average_difficulty, 2),
                "total_reviews": i.total_reviews,
                "in_database": True
            })
        
        # If requested, include interviewer names from interviews/rounds that aren't in the database yet
        if include_suggestions:
            # Get unique interviewer names from interview_round table
            round_names = db.session.query(
                InterviewRound.interviewer_name,
                Interview.company_name
            ).join(Interview).filter(
                InterviewRound.interviewer_name.isnot(None),
                InterviewRound.interviewer_name != ''
            ).distinct().all()
            
            # Get unique interviewer names from interview table
            interview_names = db.session.query(
                Interview.interviewer_name,
                Interview.company_name
            ).filter(
                Interview.interviewer_name.isnot(None),
                Interview.interviewer_name != ''
            ).distinct().all()
            
            # Combine and deduplicate
            all_names = set()
            for name, company in round_names + interview_names:
                if name and company:
                    # Check if already in database
                    exists = any(i['name'] == name and i['company'] == company for i in result)
                    if not exists:
                        # Apply search filter if provided
                        if not search or search.lower() in name.lower() or search.lower() in company.lower():
                            all_names.add((name, company))
            
            # Add suggestions to result
            for name, company in sorted(all_names):
                result.append({
                    "id": None,
                    "name": name,
                    "company": company,
                    "average_difficulty": 0.0,
                    "total_reviews": 0,
                    "in_database": False,
                    "suggestion": True
                })
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"message": f"Error fetching interviewers: {str(e)}"}), 500

@routes.route('/api/interviewers/<int:interviewer_id>', methods=['GET'])
def get_interviewer(interviewer_id):
    try:
        interviewer = Interviewer.query.get(interviewer_id)
        
        if not interviewer:
            return jsonify({"message": "Interviewer not found"}), 404
        
        # Get all ratings for this interviewer, sorted by newest first
        ratings = InterviewerRating.query.filter_by(interviewer_id=interviewer_id)\
            .order_by(InterviewerRating.created_at.desc()).all()
        
        ratings_list = []
        for rating in ratings:
            user = User.query.get(rating.user_id)
            ratings_list.append({
                "id": rating.id,
                "rating": rating.rating,
                "comments": rating.comments,
                "created_at": rating.created_at.isoformat(),
                "username": user.username if user else "Unknown"
            })
        
        result = {
            "id": interviewer.id,
            "name": interviewer.name,
            "company": interviewer.company,
            "average_difficulty": round(interviewer.average_difficulty, 2),
            "total_reviews": interviewer.total_reviews,
            "ratings": ratings_list
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"message": f"Error fetching interviewer: {str(e)}"}), 500

@routes.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    # Ensure username and password are provided
    username = data.get('username', None)
    password = data.get('password', None)
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    # Look up the user in the database
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401

    # Create a new access token with an optional expiration time
    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))
    return jsonify(access_token=access_token), 200

@routes.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()

    # Extract required fields
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"msg": "Missing username, email, or password"}), 400

    # Check if a user with the same username or email exists
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"msg": "User already exists"}), 400

    # Create a new user and set the password
    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201